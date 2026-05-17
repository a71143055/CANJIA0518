from flask import Flask, render_template, redirect, url_for, request, session, flash
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from authlib.integrations.flask_client import OAuth
from models import db, User, Field, Document, FieldMembership
from config import Config
import requests
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

# OAuth setup
oauth = OAuth(app)
microsoft = oauth.register(
    'microsoft',
    client_id=Config.MICROSOFT_CLIENT_ID,
    client_secret=Config.MICROSOFT_CLIENT_SECRET,
    server_metadata_url=f'https://login.microsoftonline.com/{Config.MICROSOFT_TENANT_ID}/v2.0/.well-known/openid-configuration',
    client_kwargs={'scope': 'openid profile email'}
)

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

@app.route('/login')
def login():
    """Login page with Microsoft OAuth"""
    redirect_uri = url_for('auth_callback', _external=True)
    return microsoft.authorize_redirect(redirect_uri)

@app.route('/auth/callback')
def auth_callback():
    """Microsoft OAuth callback"""
    token = microsoft.authorize_access_token()
    resp = microsoft.get('https://graph.microsoft.com/v1.0/me')
    user_info = resp.json()
    
    # Check if user exists
    user = User.query.filter_by(microsoft_id=user_info['id']).first()
    
    if not user:
        # Create new user
        user = User(
            microsoft_id=user_info['id'],
            email=user_info['mail'] or user_info['userPrincipalName'],
            name=user_info['displayName'],
            profile_image=user_info.get('photo', '')
        )
        db.session.add(user)
        db.session.commit()
    
    login_user(user)
    return redirect(url_for('dashboard'))

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
