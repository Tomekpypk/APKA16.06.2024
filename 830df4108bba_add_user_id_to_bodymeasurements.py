"""Add user_id to BodyMeasurements

Revision ID: 830df4108bba
Revises: d156eea912f3
Create Date: 2024-06-26 11:54:34.535987

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '830df4108bba'
down_revision = 'd156eea912f3'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('body_measurements', schema=None) as batch_op:
        batch_op.add_column(sa.Column('user_id', sa.Integer(), nullable=False))
        batch_op.create_foreign_key('fk_user_id', 'user', ['user_id'], ['id'])

def downgrade():
    with op.batch_alter_table('body_measurements', schema=None) as batch_op:
        batch_op.drop_constraint('fk_user_id', type_='foreignkey')
        batch_op.drop_column('user_id')

#PLIK DO MIGRACJI
