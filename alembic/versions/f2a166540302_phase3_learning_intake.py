"""phase3 learning intake
Revision ID: f2a166540302
Revises: 1e944b674f6b
"""
from alembic import op
import sqlalchemy as sa
revision='f2a166540302'; down_revision='1e944b674f6b'; branch_labels=None; depends_on=None

def upgrade():
    op.create_table('college_courses',sa.Column('id',sa.String(36),primary_key=True),sa.Column('user_id',sa.String(36),sa.ForeignKey('users.id'),nullable=False),sa.Column('code',sa.String(80),nullable=False),sa.Column('title',sa.String(300),nullable=False),sa.Column('term',sa.String(120)),sa.Column('active',sa.Boolean(),nullable=False),sa.Column('created_at',sa.DateTime(),nullable=False),sa.UniqueConstraint('user_id','code','term'))
    op.create_index('ix_college_courses_user_id','college_courses',['user_id'])
    op.create_table('external_learning_events',sa.Column('id',sa.String(36),primary_key=True),sa.Column('user_id',sa.String(36),sa.ForeignKey('users.id'),nullable=False),sa.Column('source',sa.String(200),nullable=False),sa.Column('topic',sa.String(300),nullable=False),sa.Column('covered',sa.Text(),nullable=False),sa.Column('source_url',sa.String(1000)),sa.Column('minutes',sa.Integer()),sa.Column('status',sa.String(40),nullable=False),sa.Column('created_at',sa.DateTime(),nullable=False))
    op.create_index('ix_external_learning_events_user_id','external_learning_events',['user_id'])
    op.create_table('assignments',sa.Column('id',sa.String(36),primary_key=True),sa.Column('user_id',sa.String(36),sa.ForeignKey('users.id'),nullable=False),sa.Column('college_course_id',sa.String(36),sa.ForeignKey('college_courses.id')),sa.Column('title',sa.String(300),nullable=False),sa.Column('notes',sa.Text(),nullable=False),sa.Column('due_at',sa.DateTime()),sa.Column('status',sa.String(40),nullable=False),sa.Column('created_at',sa.DateTime(),nullable=False))
    op.create_index('ix_assignments_user_id','assignments',['user_id']); op.create_index('ix_assignments_college_course_id','assignments',['college_course_id'])
    op.create_table('assignment_items',sa.Column('id',sa.String(36),primary_key=True),sa.Column('assignment_id',sa.String(36),sa.ForeignKey('assignments.id'),nullable=False),sa.Column('position',sa.Integer(),nullable=False),sa.Column('prompt',sa.Text(),nullable=False),sa.Column('concept_ids',sa.JSON(),nullable=False),sa.Column('help_level',sa.Integer(),nullable=False),sa.Column('completed',sa.Boolean(),nullable=False))
    op.create_index('ix_assignment_items_assignment_id','assignment_items',['assignment_id'])
    op.create_table('learning_resources',sa.Column('id',sa.String(36),primary_key=True),sa.Column('user_id',sa.String(36),sa.ForeignKey('users.id'),nullable=False),sa.Column('title',sa.String(300),nullable=False),sa.Column('resource_type',sa.String(40),nullable=False),sa.Column('url',sa.String(1000)),sa.Column('file_id',sa.String(36),sa.ForeignKey('files.id')),sa.Column('concept_ids',sa.JSON(),nullable=False),sa.Column('metadata_json',sa.JSON(),nullable=False),sa.Column('created_at',sa.DateTime(),nullable=False))
    op.create_index('ix_learning_resources_user_id','learning_resources',['user_id'])
    op.create_table('media_usage_events',sa.Column('id',sa.String(36),primary_key=True),sa.Column('user_id',sa.String(36),sa.ForeignKey('users.id'),nullable=False),sa.Column('resource_id',sa.String(36),sa.ForeignKey('learning_resources.id'),nullable=False),sa.Column('action',sa.String(40),nullable=False),sa.Column('seconds',sa.Integer()),sa.Column('created_at',sa.DateTime(),nullable=False))
    op.create_index('ix_media_usage_events_user_id','media_usage_events',['user_id']); op.create_index('ix_media_usage_events_resource_id','media_usage_events',['resource_id'])
    op.create_table('learner_notes',sa.Column('id',sa.String(36),primary_key=True),sa.Column('user_id',sa.String(36),sa.ForeignKey('users.id'),nullable=False),sa.Column('body',sa.Text(),nullable=False),sa.Column('course_id',sa.String(36)),sa.Column('lesson_id',sa.String(36)),sa.Column('concept_id',sa.String(36)),sa.Column('created_at',sa.DateTime(),nullable=False))
    op.create_index('ix_learner_notes_user_id','learner_notes',['user_id'])

def downgrade():
    for t in ['learner_notes','media_usage_events','learning_resources','assignment_items','assignments','external_learning_events','college_courses']:
        op.drop_table(t)
