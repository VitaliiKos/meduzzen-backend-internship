"""notification_CASCADE

Revision ID: 76b133c74fc0
Revises: 2edf95d51116
Create Date: 2023-09-10 16:59:03.201322

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '76b133c74fc0'
down_revision = '2edf95d51116'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('notification_table_user_id_fkey', 'notification_table', type_='foreignkey')
    op.drop_constraint('notification_table_quiz_id_fkey', 'notification_table', type_='foreignkey')
    op.create_foreign_key(None, 'notification_table', 'quiz_table', ['quiz_id'], ['id'], ondelete='CASCADE')
    op.create_foreign_key(None, 'notification_table', 'user_table', ['user_id'], ['id'], ondelete='CASCADE')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'notification_table', type_='foreignkey')
    op.drop_constraint(None, 'notification_table', type_='foreignkey')
    op.create_foreign_key('notification_table_quiz_id_fkey', 'notification_table', 'quiz_table', ['quiz_id'], ['id'])
    op.create_foreign_key('notification_table_user_id_fkey', 'notification_table', 'user_table', ['user_id'], ['id'])
    # ### end Alembic commands ###
