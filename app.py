from flask import Flask, render_template, redirect, url_for, request, session, flash
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from models import db, User, Field, Document, FieldMembership
from config import Config
import pyotp
import qrcode
import io
import base64
import json
from datetime import datetime

app = Flask(__name__)
app.config.from_object(Config)

# Custom filter for newline to br
@app.template_filter('nl2br')
def nl2br(text):
    if text is None:
        return ''
    return text.replace('\n', '<br>')

# Initialize extensions
db.init_app(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message = '로그인이 필요합니다.'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def init_fields():
    """Initialize fields in database"""
    for field_config in Config.FIELDS:
        if not Field.query.filter_by(field_id=field_config['id']).first():
            field = Field(
                field_id=field_config['id'],
                name=field_config['name'],
                description=field_config['description']
            )
            db.session.add(field)
    db.session.commit()

@app.route('/')
def index():
    """Main landing page"""
    return render_template('index.html', fields=Config.FIELDS, goals=Config.GOALS)

@app.route('/register', methods=['GET', 'POST'])
def register():
    """User registration"""
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        name = request.form['name']
        
        # Check if user already exists
        if User.query.filter_by(username=username).first():
            flash('이미 존재하는 사용자 이름입니다.')
            return redirect(url_for('register'))
        
        if User.query.filter_by(email=email).first():
            flash('이미 존재하는 이메일입니다.')
            return redirect(url_for('register'))
        
        # Create new user
        user = User(
            username=username,
            email=email,
            name=name
        )
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        
        flash('회원가입이 완료되었습니다. 로그인해주세요.')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login"""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            if user.two_factor_enabled:
                # Store user ID in session for 2FA verification
                session['pending_user_id'] = user.id
                return redirect(url_for('two_factor_verify'))
            else:
                login_user(user)
                return redirect(url_for('dashboard'))
        else:
            flash('사용자 이름 또는 비밀번호가 올바르지 않습니다.')
    
    return render_template('login.html')

@app.route('/two-factor/verify', methods=['GET', 'POST'])
def two_factor_verify():
    """Verify 2FA code"""
    if 'pending_user_id' not in session:
        return redirect(url_for('login'))
    
    user = User.query.get(session['pending_user_id'])
    if not user:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        code = request.form['code']
        
        # Verify TOTP code
        totp = pyotp.TOTP(user.two_factor_secret)
        if totp.verify(code):
            login_user(user)
            session.pop('pending_user_id')
            return redirect(url_for('dashboard'))
        else:
            flash('인증 코드가 올바르지 않습니다.')
    
    return render_template('two_factor_verify.html')

@app.route('/two-factor/setup', methods=['GET', 'POST'])
@login_required
def two_factor_setup():
    """Setup 2FA for user"""
    if request.method == 'POST':
        # Generate secret
        secret = pyotp.random_base32()
        current_user.two_factor_secret = secret
        
        # Generate backup codes
        backup_codes = [pyotp.random_base32()[:8] for _ in range(10)]
        current_user.two_factor_backup_codes = json.dumps(backup_codes)
        
        db.session.commit()
        
        # Generate QR code
        totp = pyotp.TOTP(secret)
        qr_uri = totp.provisioning_uri(
            name=current_user.email,
            issuer_name='CANJIA'
        )
        
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(qr_uri)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Convert to base64
        img_io = io.BytesIO()
        img.save(img_io, 'PNG')
        img_io.seek(0)
        img_base64 = base64.b64encode(img_io.getvalue()).decode()
        
        return render_template('two_factor_setup.html', 
                             qr_code=img_base64, 
                             secret=secret,
                             backup_codes=backup_codes,
                             show_confirmation=True)
    
    return render_template('two_factor_setup.html', show_confirmation=False)

@app.route('/two-factor/confirm', methods=['POST'])
@login_required
def two_factor_confirm():
    """Confirm 2FA setup"""
    code = request.form['code']
    
    totp = pyotp.TOTP(current_user.two_factor_secret)
    if totp.verify(code):
        current_user.two_factor_enabled = True
        db.session.commit()
        flash('2차 인증이 활성화되었습니다.')
        return redirect(url_for('profile'))
    else:
        flash('인증 코드가 올바르지 않습니다. 다시 시도해주세요.')
        return redirect(url_for('two_factor_setup'))

@app.route('/two-factor/disable', methods=['POST'])
@login_required
def two_factor_disable():
    """Disable 2FA"""
    current_user.two_factor_enabled = False
    current_user.two_factor_secret = None
    current_user.two_factor_backup_codes = None
    db.session.commit()
    flash('2차 인증이 비활성화되었습니다.')
    return redirect(url_for('profile'))

@app.route('/logout')
@login_required
def logout():
    """Logout user"""
    logout_user()
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    """User dashboard"""
    user_fields = [fm.field for fm in current_user.field_memberships]
    user_documents = Document.query.filter_by(user_id=current_user.id).order_by(Document.updated_at.desc()).all()
    return render_template('dashboard.html', user=current_user, fields=Config.FIELDS, user_fields=user_fields, user_documents=user_documents)

@app.route('/profile')
@login_required
def profile():
    """User profile page"""
    return render_template('profile.html', user=current_user)

@app.route('/profile/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    """Edit user profile"""
    if request.method == 'POST':
        current_user.bio = request.form.get('bio', '')
        db.session.commit()
        flash('프로필이 업데이트되었습니다.')
        return redirect(url_for('profile'))
    return render_template('edit_profile.html', user=current_user)

@app.route('/field/<field_id>')
@login_required
def field_detail(field_id):
    """Field detail page with documents"""
    field = Field.query.filter_by(field_id=field_id).first_or_404()
    documents = Document.query.filter_by(field_id=field.id, is_public=True).order_by(Document.updated_at.desc()).all()
    
    # Check if user is member of this field
    is_member = FieldMembership.query.filter_by(user_id=current_user.id, field_id=field.id).first() is not None
    
    field_config = next((f for f in Config.FIELDS if f['id'] == field_id), None)
    return render_template('field_detail.html', field=field, documents=documents, is_member=is_member, field_config=field_config)

@app.route('/field/<field_id>/join', methods=['POST'])
@login_required
def join_field(field_id):
    """Join a field"""
    field = Field.query.filter_by(field_id=field_id).first_or_404()
    
    # Check if already member
    existing = FieldMembership.query.filter_by(user_id=current_user.id, field_id=field.id).first()
    if not existing:
        membership = FieldMembership(user_id=current_user.id, field_id=field.id)
        db.session.add(membership)
        db.session.commit()
        flash(f'{field.name} 분야에 가입되었습니다.')
    else:
        flash('이미 가입된 분야입니다.')
    
    return redirect(url_for('field_detail', field_id=field_id))

@app.route('/field/<field_id>/leave', methods=['POST'])
@login_required
def leave_field(field_id):
    """Leave a field"""
    field = Field.query.filter_by(field_id=field_id).first_or_404()
    membership = FieldMembership.query.filter_by(user_id=current_user.id, field_id=field.id).first()
    
    if membership:
        db.session.delete(membership)
        db.session.commit()
        flash(f'{field.name} 분야에서 탈퇴했습니다.')
    
    return redirect(url_for('field_detail', field_id=field_id))

@app.route('/document/new/<field_id>', methods=['GET', 'POST'])
@login_required
def new_document(field_id):
    """Create new document"""
    field = Field.query.filter_by(field_id=field_id).first_or_404()
    
    # Check if user is member
    is_member = FieldMembership.query.filter_by(user_id=current_user.id, field_id=field.id).first() is not None
    if not is_member:
        flash('문서를 작성하려면 해당 분야에 가입해야 합니다.')
        return redirect(url_for('field_detail', field_id=field_id))
    
    if request.method == 'POST':
        document = Document(
            title=request.form['title'],
            content=request.form['content'],
            user_id=current_user.id,
            field_id=field.id,
            is_public=request.form.get('is_public') == 'on'
        )
        db.session.add(document)
        db.session.commit()
        flash('문서가 생성되었습니다.')
        return redirect(url_for('document_detail', document_id=document.id))
    
    return render_template('edit_document.html', field=field, document=None)

@app.route('/document/<int:document_id>')
@login_required
def document_detail(document_id):
    """View document detail"""
    document = Document.query.get_or_404(document_id)
    
    # Check access permission
    if not document.is_public and document.user_id != current_user.id:
        flash('접근 권한이 없습니다.')
        return redirect(url_for('dashboard'))
    
    return render_template('document_detail.html', document=document)

@app.route('/document/<int:document_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_document(document_id):
    """Edit document"""
    document = Document.query.get_or_404(document_id)
    
    # Check ownership
    if document.user_id != current_user.id:
        flash('수정 권한이 없습니다.')
        return redirect(url_for('document_detail', document_id=document_id))
    
    if request.method == 'POST':
        document.title = request.form['title']
        document.content = request.form['content']
        document.is_public = request.form.get('is_public') == 'on'
        document.updated_at = datetime.utcnow()
        db.session.commit()
        flash('문서가 업데이트되었습니다.')
        return redirect(url_for('document_detail', document_id=document_id))
    
    return render_template('edit_document.html', field=document.field, document=document)

@app.route('/document/<int:document_id>/delete', methods=['POST'])
@login_required
def delete_document(document_id):
    """Delete document"""
    document = Document.query.get_or_404(document_id)
    
    # Check ownership
    if document.user_id != current_user.id:
        flash('삭제 권한이 없습니다.')
        return redirect(url_for('document_detail', document_id=document_id))
    
    field_id = document.field.field_id
    db.session.delete(document)
    db.session.commit()
    flash('문서가 삭제되었습니다.')
    return redirect(url_for('field_detail', field_id=field_id))

@app.route('/my-documents')
@login_required
def my_documents():
    """View all user's documents"""
    documents = Document.query.filter_by(user_id=current_user.id).order_by(Document.updated_at.desc()).all()
    return render_template('my_documents.html', documents=documents)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        init_fields()
    app.run(debug=True)
