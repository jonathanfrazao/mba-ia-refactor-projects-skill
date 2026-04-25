import logging
from datetime import datetime
from sqlalchemy.orm import joinedload
from database import db
from models.task import Task
from models.user import User
from models.category import Category
from utils.helpers import (
    VALID_STATUSES, MAX_TITLE_LENGTH, MIN_TITLE_LENGTH,
    DEFAULT_PRIORITY, parse_date
)

logger = logging.getLogger(__name__)


def get_all_tasks():
    tasks = Task.query.options(
        joinedload(Task.user),
        joinedload(Task.category)
    ).all()
    result = []
    for t in tasks:
        data = t.to_dict()
        data['overdue'] = t.is_overdue()
        data['user_name'] = t.user.name if t.user else None
        data['category_name'] = t.category.name if t.category else None
        result.append(data)
    return result


def get_task(task_id):
    task = db.session.get(Task, task_id)
    if not task:
        return None
    data = task.to_dict()
    data['overdue'] = task.is_overdue()
    return data


def create_task(data):
    title = data.get('title', '')
    if isinstance(title, str):
        title = title.strip()
    if not title:
        raise ValueError('Título é obrigatório')
    if len(title) < MIN_TITLE_LENGTH:
        raise ValueError('Título muito curto')
    if len(title) > MAX_TITLE_LENGTH:
        raise ValueError('Título muito longo')

    status = data.get('status', 'pending')
    if status not in VALID_STATUSES:
        raise ValueError('Status inválido')

    priority = data.get('priority', DEFAULT_PRIORITY)
    if not isinstance(priority, int) or priority < 1 or priority > 5:
        raise ValueError('Prioridade deve ser entre 1 e 5')

    user_id = data.get('user_id')
    if user_id and not db.session.get(User, user_id):
        raise ValueError('Usuário não encontrado')

    category_id = data.get('category_id')
    if category_id and not db.session.get(Category, category_id):
        raise ValueError('Categoria não encontrada')

    task = Task(
        title=title,
        description=data.get('description', ''),
        status=status,
        priority=priority,
        user_id=user_id,
        category_id=category_id
    )

    due_date = data.get('due_date')
    if due_date:
        parsed = parse_date(due_date) if isinstance(due_date, str) else due_date
        if not parsed:
            raise ValueError('Formato de data inválido. Use YYYY-MM-DD')
        task.due_date = parsed

    tags = data.get('tags')
    if tags:
        task.tags = ','.join(tags) if isinstance(tags, list) else tags

    db.session.add(task)
    db.session.commit()
    logger.info(f"Task criada: id={task.id} title={task.title!r}")
    return task.to_dict()


def update_task(task_id, data):
    task = db.session.get(Task, task_id)
    if not task:
        return None

    if 'title' in data:
        title = data['title'].strip()
        if len(title) < MIN_TITLE_LENGTH:
            raise ValueError('Título muito curto')
        if len(title) > MAX_TITLE_LENGTH:
            raise ValueError('Título muito longo')
        task.title = title

    if 'description' in data:
        task.description = data['description']

    if 'status' in data:
        if data['status'] not in VALID_STATUSES:
            raise ValueError('Status inválido')
        task.status = data['status']

    if 'priority' in data:
        p = data['priority']
        if not isinstance(p, int) or p < 1 or p > 5:
            raise ValueError('Prioridade deve ser entre 1 e 5')
        task.priority = p

    if 'user_id' in data:
        if data['user_id'] and not db.session.get(User, data['user_id']):
            raise ValueError('Usuário não encontrado')
        task.user_id = data['user_id']

    if 'category_id' in data:
        if data['category_id'] and not db.session.get(Category, data['category_id']):
            raise ValueError('Categoria não encontrada')
        task.category_id = data['category_id']

    if 'due_date' in data:
        if data['due_date']:
            parsed = parse_date(data['due_date']) if isinstance(data['due_date'], str) else data['due_date']
            if not parsed:
                raise ValueError('Formato de data inválido')
            task.due_date = parsed
        else:
            task.due_date = None

    if 'tags' in data:
        tags = data['tags']
        task.tags = ','.join(tags) if isinstance(tags, list) else tags

    task.updated_at = datetime.utcnow()
    db.session.commit()
    logger.info(f"Task atualizada: id={task.id}")
    return task.to_dict()


def delete_task(task_id):
    task = db.session.get(Task, task_id)
    if not task:
        return False
    db.session.delete(task)
    db.session.commit()
    logger.info(f"Task deletada: id={task_id}")
    return True


def search_tasks(query='', status='', priority='', user_id=''):
    q = Task.query
    if query:
        q = q.filter(
            db.or_(
                Task.title.like(f'%{query}%'),
                Task.description.like(f'%{query}%')
            )
        )
    if status:
        q = q.filter(Task.status == status)
    if priority:
        q = q.filter(Task.priority == int(priority))
    if user_id:
        q = q.filter(Task.user_id == int(user_id))
    return [t.to_dict() for t in q.all()]


def get_task_stats():
    total = Task.query.count()
    pending = Task.query.filter_by(status='pending').count()
    in_progress = Task.query.filter_by(status='in_progress').count()
    done = Task.query.filter_by(status='done').count()
    cancelled = Task.query.filter_by(status='cancelled').count()
    overdue_count = sum(1 for t in Task.query.all() if t.is_overdue())
    return {
        'total': total,
        'pending': pending,
        'in_progress': in_progress,
        'done': done,
        'cancelled': cancelled,
        'overdue': overdue_count,
        'completion_rate': round((done / total) * 100, 2) if total > 0 else 0
    }
