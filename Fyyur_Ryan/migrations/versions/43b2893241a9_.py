"""empty message

Revision ID: 43b2893241a9
Revises: 232d6ac191b5
Create Date: 2022-11-01 09:44:58.340381

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '43b2893241a9'
down_revision = '232d6ac191b5'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('Show',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('start_time', sa.DateTime(), nullable=False),
    sa.Column('venue_id', sa.Integer(), nullable=False),
    sa.Column('artist_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['artist_id'], ['Artist.id'], ),
    sa.ForeignKeyConstraint(['venue_id'], ['Venue.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.add_column('Artist', sa.Column('website_link', sa.String(), nullable=True))
    op.add_column('Artist', sa.Column('looking_venues', sa.Boolean(), nullable=True))
    op.add_column('Artist', sa.Column('seeking_description', sa.String(), nullable=True))
    op.add_column('Venue', sa.Column('genres', sa.ARRAY(sa.String()), nullable=True))
    op.add_column('Venue', sa.Column('website_link', sa.String(), nullable=True))
    op.add_column('Venue', sa.Column('looking_talent', sa.Boolean(), nullable=True))
    op.add_column('Venue', sa.Column('seeking_description', sa.String(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('Venue', 'seeking_description')
    op.drop_column('Venue', 'looking_talent')
    op.drop_column('Venue', 'website_link')
    op.drop_column('Venue', 'genres')
    op.drop_column('Artist', 'seeking_description')
    op.drop_column('Artist', 'looking_venues')
    op.drop_column('Artist', 'website_link')
    op.drop_table('Show')
    # ### end Alembic commands ###
