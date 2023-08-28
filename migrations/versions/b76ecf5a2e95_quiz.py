"""quiz

Revision ID: b76ecf5a2e95
Revises: 67d12defff9d
Create Date: 2023-08-28 13:58:24.613537

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b76ecf5a2e95'
down_revision = '67d12defff9d'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('quiz_table',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('company_id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('title', sa.String(), nullable=False),
    sa.Column('description', sa.String(), nullable=True),
    sa.Column('frequency_in_days', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['company_id'], ['company_table.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['user_table.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_quiz_table_id'), 'quiz_table', ['id'], unique=False)
    op.create_table('question_table',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('quiz_id', sa.Integer(), nullable=False),
    sa.Column('question_text', sa.String(), nullable=False),
    sa.ForeignKeyConstraint(['quiz_id'], ['quiz_table.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_question_table_id'), 'question_table', ['id'], unique=False)
    op.create_table('answer_table',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('question_id', sa.Integer(), nullable=False),
    sa.Column('answer_text', sa.String(), nullable=False),
    sa.Column('is_correct', sa.BOOLEAN(), nullable=True),
    sa.ForeignKeyConstraint(['question_id'], ['question_table.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_answer_table_id'), 'answer_table', ['id'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_answer_table_id'), table_name='answer_table')
    op.drop_table('answer_table')
    op.drop_index(op.f('ix_question_table_id'), table_name='question_table')
    op.drop_table('question_table')
    op.drop_index(op.f('ix_quiz_table_id'), table_name='quiz_table')
    op.drop_table('quiz_table')
    # ### end Alembic commands ###
