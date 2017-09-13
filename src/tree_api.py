from flask import Blueprint, jsonify
from flask_login import login_required

from sql import getResults, getSingleResult, getOption

tree_api = Blueprint('tree_api', __name__)

@tree_api.route('/tree', methods = ['GET'])
@login_required
def getTree():
    notes = getResults("select "
                       "notes_tree.*, "
                       "COALESCE(clone.note_title, notes.note_title) as note_title, "
                       "notes.note_clone_id, "
                       "notes.encryption, "
                       "case when notes.note_clone_id is null or notes.note_clone_id = '' then 0 else 1 end as is_clone "
                       "from notes_tree "
                       "join notes on notes.note_id = notes_tree.note_id "
                       "left join notes as clone on notes.note_clone_id = clone.note_id "
                       "order by note_pid, note_pos")

    rootNotes = []
    notesMap = {}

    for note in notes:
        note['children'] = []

        if not note['note_pid']:
            rootNotes.append(note)

        notesMap[note['note_id']] = note

    for note in notes:
        if note['note_pid'] != "":
            parent = notesMap[note['note_pid']]

            parent['children'].append(note)
            parent['folder'] = True

    retObject = {}
    retObject['notes'] = rootNotes
    retObject['start_note_id'] = getSingleResult('select * from options where opt_name = "start_node"')['opt_value'];
    retObject['verification_salt'] = getOption('verification_salt')
    retObject['encryption_salt'] = getOption('encryption_salt')

    return jsonify(retObject)