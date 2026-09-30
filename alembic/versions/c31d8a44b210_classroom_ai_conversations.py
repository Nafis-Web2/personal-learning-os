
"""classroom ai conversations
Revision ID: c31d8a44b210
Revises: a91c44e7f802
"""
from alembic import op
import sqlalchemy as sa
revision='c31d8a44b210';down_revision='a91c44e7f802';branch_labels=None;depends_on=None
def upgrade():
    op.create_table('tutor_interactions',
      sa.Column('id',sa.String(36),primary_key=True),
      sa.Column('user_id',sa.String(36),sa.ForeignKey('users.id'),nullable=False),
      sa.Column('course_id',sa.String(36),sa.ForeignKey('courses.id')),
      sa.Column('lesson_id',sa.String(36),sa.ForeignKey('lessons.id')),
      sa.Column('concept_id',sa.String(36),sa.ForeignKey('concepts.id')),
      sa.Column('mode',sa.String(32),nullable=False),
      sa.Column('help_level',sa.Integer(),nullable=False),
      sa.Column('learner_input',sa.Text(),nullable=False),
      sa.Column('tutor_output',sa.Text(),nullable=False),
      sa.Column('provider',sa.String(40),nullable=False),
      sa.Column('model_name',sa.String(120),nullable=False),
      sa.Column('fallback',sa.Boolean(),nullable=False),
      sa.Column('created_at',sa.DateTime(),nullable=False))
    op.create_index('ix_tutor_interactions_user_id','tutor_interactions',['user_id'])
    op.create_index('ix_tutor_interactions_course_id','tutor_interactions',['course_id'])
    op.create_index('ix_tutor_interactions_created_at','tutor_interactions',['created_at'])
def downgrade():
    op.drop_index('ix_tutor_interactions_created_at',table_name='tutor_interactions')
    op.drop_index('ix_tutor_interactions_course_id',table_name='tutor_interactions')
    op.drop_index('ix_tutor_interactions_user_id',table_name='tutor_interactions')
    op.drop_table('tutor_interactions')
