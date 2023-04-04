import firebase_admin
from firebase_admin import credentials, firestore
import json
from flask import Flask, request, jsonify

# Use a service account.
cred = credentials.Certificate("forward-garden-381416-firebase-adminsdk-9wmuy-2980fe1b6f.json")
firebase_app = firebase_admin.initialize_app(cred)
db = firestore.client()

app = Flask(__name__)                        


'''VOTERS'''
voters = db.collection(u'voters')

# Registering a student as a voter
@app.route('/voters', methods=['POST'])
def create_voter(request):
    voter_id = request.json.get('ID')
    voter = voters.document(voter_id).get()
    if voter.exists:
        return jsonify({'error' : 'voter already exists'}), 409
    else:
        voters.document(voter_id).set(request.json)
        return jsonify(request.json), 201





# Retrieving a registered voter
@app.route('/voters', methods=['GET'])
def get_voter(request):
    voter_id=request.args.get("voter_id")
    voter_ref = voters.document(voter_id)
    voter = voter_ref.get()
    if not voter.exists:
        return jsonify({'error': 'voter does not exist'}), 404
    else:
        return jsonify(voter.to_dict()), 200


# De-registering a Student as a Voter
@app.route('/voters/<voter_id>', methods=['DELETE'])
def delete_voter(request):
    voter_id = request.args.get("voter_id") 
    voter_ref = voters.document(voter_id)
    voter = voter_ref.get()
    if not voter.exists:
        return jsonify({'error': 'voter does not exist'}), 404
    else:
        voter_ref.delete()
        return '', 204




# Updating a Registered Voter's Information
@app.route('/voters/<voter_id>', methods=['PUT'])
def update_voter(request):
    voter_id=request.args.get("voter_id")
    voter_ref = voters.document(voter_id)
    voter = voter_ref.get()
    if not voter.exists:
        return jsonify({'error': 'voter does not exist'}), 404
    else:
        voter_ref.update(request.json)
        return jsonify(request.json), 200




'''ELECTIONS'''
elections = db.collection(u'elections')

# Creating an Election
@app.route('/elections', methods=['POST'])
def create_election():
    record = json.loads(request.data)
    election_id = record["ID"]
    election_ref = elections.document(election_id)
    
    if election_ref.get().exists:
        return jsonify({'error': 'election already exists'}), 409
    else:
        election_ref.set(record)
        return jsonify(record), 201



# Retrieving an Election
@app.route('/elections/<election_id>', methods=['GET'])
def get_election(request):
    election_id = request.args.get('electionID')
    election_ref = elections.document(election_id)
    election = election_ref.get()
    if not election.exists:
        return jsonify({'error': 'election does not exist'}), 404
    
    election_data = election.to_dict()
    return jsonify(election_data), 200




# Deleting an Election
@app.route('/elections/<election_id>', methods=['DELETE'])
def delete_election(request):
    election_id = request.args.get('electionID')
    election_ref = elections.document(election_id)
    election = election_ref.get()
    if not election.exists:
        return jsonify({'error': 'election does not exist'}), 404
    else:
        election_ref.delete()
        return jsonify({'message': 'election deleted successfully'}), 200




# Voting in an Election
@app.route('/elections/<election_id>/<candidate_id>', methods=['PATCH'])
def vote(request):
    # Check if the election exists
    election_id = request.args.get('electionID')
    candidate_id = request.args.get('candidate_id')
    election_ref = elections.document(election_id)
    election_doc = election_ref.get()
    if not election_doc.exists:
        return jsonify({"error": "election not found"}), 404    
    # Check if the candidate exists in the election
    candidates = election_doc.to_dict().get('candidates', [])
    candidate_ref = None
    for candidate in candidates:
        if candidate['candidateID'] == candidate_id:
            candidate_ref = election_ref.collection('candidates').document(candidate_id)
            break
    if candidate_ref is None:
        return jsonify({"error": "candidate not found"}), 404
    
    # Update the candidate's vote count
    candidate_ref.update({'votesCast': firestore.Increment(1)})
    
    return jsonify({'success': True}), 200



