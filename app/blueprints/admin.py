from flask import Blueprint, abort
from app.models import User
from flask_login import current_user
from app.extensions import db

admin_bp = Blueprint('admin', __name__)


@admin_bp.route('/delete_user/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    if not current_user.is_admin:
        abort(403)

    if user.is_admin:
        abort(400)

    db.session.delete(user)
    db.session.commit()
    return '', 204

