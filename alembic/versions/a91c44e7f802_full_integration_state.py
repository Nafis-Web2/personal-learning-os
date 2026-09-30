"""full integration persistent state
Revision ID: a91c44e7f802
Revises: f2a166540302
"""
from alembic import op
import sqlalchemy as sa
revision='a91c44e7f802'; down_revision='f2a166540302'; branch_labels=None; depends_on=None

def upgrade():
    op.create_table('personalization_snapshots',
        sa.Column('id',sa.String(36),primary_key=True),sa.Column('user_id',sa.String(36),sa.ForeignKey('users.id'),nullable=False),
        sa.Column('concept_id',sa.String(36),sa.ForeignKey('concepts.id')),sa.Column('profile_json',sa.JSON(),nullable=False),
        sa.Column('reason_codes',sa.JSON(),nullable=False),sa.Column('created_at',sa.DateTime(),nullable=False))
    op.create_index('ix_personalization_snapshots_user_id','personalization_snapshots',['user_id'])
    op.create_index('ix_personalization_snapshots_concept_id','personalization_snapshots',['concept_id'])
    op.create_table('application_attempts',
        sa.Column('id',sa.String(36),primary_key=True),sa.Column('user_id',sa.String(36),sa.ForeignKey('users.id'),nullable=False),
        sa.Column('concept_id',sa.String(36),sa.ForeignKey('concepts.id')),sa.Column('attempt_type',sa.String(40),nullable=False),
        sa.Column('help_level',sa.Integer(),nullable=False),sa.Column('score',sa.Float()),sa.Column('process_json',sa.JSON(),nullable=False),
        sa.Column('outcome_json',sa.JSON(),nullable=False),sa.Column('created_at',sa.DateTime(),nullable=False))
    op.create_index('ix_application_attempts_user_id','application_attempts',['user_id'])
    op.create_index('ix_application_attempts_concept_id','application_attempts',['concept_id'])

def downgrade():
    op.drop_index('ix_application_attempts_concept_id',table_name='application_attempts');op.drop_index('ix_application_attempts_user_id',table_name='application_attempts');op.drop_table('application_attempts')
    op.drop_index('ix_personalization_snapshots_concept_id',table_name='personalization_snapshots');op.drop_index('ix_personalization_snapshots_user_id',table_name='personalization_snapshots');op.drop_table('personalization_snapshots')
