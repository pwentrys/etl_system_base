__author__ = 'Przemyslaw "Blasto" Wentrys'

from flask_wtf import Form
from wtforms import TextAreaField
from wtforms.validators import DataRequired, Length


class Query(Form):
    query = TextAreaField('Custom Query',
                          id=u'query',
                          validators=[
                              DataRequired(),
                              Length(min=1, max=255)
                          ]
    )
