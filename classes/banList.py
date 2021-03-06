from .shared import db

class banList(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    channelLoc = db.Column(db.String(255))
    userID = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self,channelLoc,userID):
        self.channelLoc = channelLoc
        self.userID = userID

    def __repr__(self):
        return '<id %r>' % self.id