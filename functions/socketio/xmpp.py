from flask_security import current_user
from flask_socketio import emit
from sqlalchemy.sql.expression import func

from classes.shared import db, socketio
from classes import Channel
from classes import Sec
from classes import settings

@socketio.on('addMod')
def addMod(message):
    sysSettings = settings.settings.query.first()
    if '@' in str(message['JID']):
        JID = str(message['JID'])
    else:
        username = str(message['JID'])
        userQuery = Sec.User.query.filter(func.lower(Sec.User.username) == func.lower(username)).first()
        if userQuery is not None:
            JID = username + '@' + sysSettings.siteAddress

    channelLoc = str(message['channelLoc'])
    channelQuery = Channel.Channel.query.filter_by(channelLoc=channelLoc, owningUser=current_user.id).first()

    if channelQuery is not None and JID != "":
        from app import ejabberd
        ejabberd.set_room_affiliation(channelLoc, 'conference.' + sysSettings.siteAddress, JID, 'admin')
        emit('addMod', {'mod': str(JID),  'channelLoc':str(channelLoc)}, broadcast=False)
    else:
        pass
    db.session.commit()
    db.session.close()
    return 'OK'

@socketio.on('deleteMod')
def deleteMod(message):
    sysSettings = settings.settings.query.first()
    JID = str(message['JID'])
    channelLoc = str(message['channelLoc'])

    channelQuery = Channel.Channel.query.filter_by(channelLoc=channelLoc, owningUser=current_user.id).first()

    user = JID.split('@')[0]
    userQuery = Sec.User.query.filter(func.lower(Sec.User.username) == func.lower(user)).first()

    if channelQuery is not None:
        if userQuery and current_user != user:
            from app import ejabberd
            ejabberd.set_room_affiliation(channelLoc, 'conference.' + sysSettings.siteAddress, JID, 'member')
            emit('deleteMod', {'mod': str(JID),  'channelLoc':str(channelLoc)}, broadcast=False)
        elif userQuery is None:
            from app import ejabberd
            ejabberd.set_room_affiliation(channelLoc, 'conference.' + sysSettings.siteAddress, JID, 'none')
            emit('deleteMod', {'mod': str(JID),  'channelLoc':str(channelLoc)}, broadcast=False)
    else:
        pass
    db.session.commit()
    db.session.close()
    return 'OK'

@socketio.on('getBanList')
def socketio_xmpp_getBanList(message):
    sysSettings = settings.settings.query.first()
    affiliationList = []
    if 'channelLoc' in message:

        channelLoc = str(message['channelLoc'])
        channelQuery = Channel.Channel.query.filter_by(channelLoc=channelLoc).first()

        if channelQuery is not None:
            from app import ejabberd
            xmppQuery = ejabberd.get_room_affiliations(channelQuery.channelLoc, 'conference.' + sysSettings.siteAddress)
            for affiliation in xmppQuery['affiliations']:
                user = {}
                for entry in affiliation['affiliation']:
                    for key, value in entry.items():
                        user[key] = value
                if user['affiliation'] == "outcast":
                    affiliationList.append(user)
    emit('returnBanList', {'results': affiliationList}, broadcast=False)
    return 'OK'