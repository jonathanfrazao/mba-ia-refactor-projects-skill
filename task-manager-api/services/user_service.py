import logging
from database import db
from models.user import User
from models.task import Task
from utils.helpers import VALID_ROLES, MIN_PASSWORD_LENGTH, validate_email

logger = logging.getLogger(__name__)


def get_all_users():
    users = User.query.all()
    return [{**u.to_dict(), 'task_count': len(u.tasks)} for u in users]


def get_user(user_id):
    user = db.session.get(User, user_id)
    if not user:
        return None
    data = user.to_dict()
    data['tasks'] = [t.to_dict() for t in Task.query.filter_by(user_id=user_id).all()]
    return data


def create_user(data):
    name = data.get('name', '').strip()
    email = data.get('email', '').strip()
    password = data.get('password', '')
    role = data.get('role', 'user')

    if not name:
        raise ValueError('Nome é obrigatório')
    if not email:
        raise ValueError('Email é obrigatório')
    if not password:
        raise ValueError('Senha é obrigatória')
    if not validate_email(email):
        raise ValueError('Email inválido')
    if len(password) < MIN_PASSWORD_LENGTH:
        raise ValueError('Senha deve ter no mínimo 4 caracteres')
    if role not in VALID_ROLES:
        raise ValueError('Role inválido')
    if User.query.filter_by(email=email).first():
        raise ValueError('Email já cadastrado')

    user = User(name=name, email=email, role=role)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    logger.info(f"Usuário criado: id={user.id} name={user.name!r}")
    return user.to_dict()


def update_user(user_id, data):
    user = db.session.get(User, user_id)
    if not user:
        return None

    if 'name' in data:
        user.name = data['name']

    if 'email' in data:
        if not validate_email(data['email']):
            raise ValueError('Email inválido')
        existing = User.query.filter_by(email=data['email']).first()
        if existing and existing.id != user_id:
            raise ValueError('Email já cadastrado')
        user.email = data['email']

    if 'password' in data:
        if len(data['password']) < MIN_PASSWORD_LENGTH:
            raise ValueError('Senha muito curta')
        user.set_password(data['password'])

    if 'role' in data:
        if data['role'] not in VALID_ROLES:
            raise ValueError('Role inválido')
        user.role = data['role']

    if 'active' in data:
        user.active = data['active']

    db.session.commit()
    return user.to_dict()


def delete_user(user_id):
    user = db.session.get(User, user_id)
    if not user:
        return False
    Task.query.filter_by(user_id=user_id).delete()
    db.session.delete(user)
    db.session.commit()
    logger.info(f"Usuário deletado: id={user_id}")
    return True


def get_user_tasks(user_id):
    user = db.session.get(User, user_id)
    if not user:
        return None
    tasks = Task.query.filter_by(user_id=user_id).all()
    return [{**t.to_dict(), 'overdue': t.is_overdue()} for t in tasks]


def login(email, password):
    user = User.query.filter_by(email=email).first()
    if not user or not user.check_password(password):
        raise ValueError('Credenciais inválidas')
    if not user.active:
        raise PermissionError('Usuário inativo')
    return user.to_dict()
