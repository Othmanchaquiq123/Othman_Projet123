from flask import Flask, jsonify, request

app = Flask(__name__)

# Base de données simulée
utilisateurs = [
    {"id": 1, "nom": "Othman", "email": "othman@example.com"},
    {"id": 2, "nom": "Ahmed", "email": "ahmed@example.com"}
]

# Route pour obtenir tous les utilisateurs
@app.route('/api/utilisateurs', methods=['GET'])
def get_utilisateurs():
    return jsonify(utilisateurs), 200

# Route pour obtenir un utilisateur par ID
@app.route('/api/utilisateurs/<int:user_id>', methods=['GET'])
def get_utilisateur(user_id):
    utilisateur = next((u for u in utilisateurs if u['id'] == user_id), None)
    if utilisateur:
        return jsonify(utilisateur), 200
    return jsonify({"erreur": "Utilisateur non trouvé"}), 404

# Route pour créer un nouvel utilisateur
@app.route('/api/utilisateurs', methods=['POST'])
def create_utilisateur():
    data = request.get_json()
    if not data or 'nom' not in data or 'email' not in data:
        return jsonify({"erreur": "Données invalides"}), 400
    
    nouvel_utilisateur = {
        "id": len(utilisateurs) + 1,
        "nom": data['nom'],
        "email": data['email']
    }
    utilisateurs.append(nouvel_utilisateur)
    return jsonify(nouvel_utilisateur), 201

# Route pour mettre à jour un utilisateur
@app.route('/api/utilisateurs/<int:user_id>', methods=['PUT'])
def update_utilisateur(user_id):
    utilisateur = next((u for u in utilisateurs if u['id'] == user_id), None)
    if not utilisateur:
        return jsonify({"erreur": "Utilisateur non trouvé"}), 404
    
    data = request.get_json()
    utilisateur['nom'] = data.get('nom', utilisateur['nom'])
    utilisateur['email'] = data.get('email', utilisateur['email'])
    return jsonify(utilisateur), 200

# Route pour supprimer un utilisateur
@app.route('/api/utilisateurs/<int:user_id>', methods=['DELETE'])
def delete_utilisateur(user_id):
    global utilisateurs
    utilisateurs = [u for u in utilisateurs if u['id'] != user_id]
    return jsonify({"message": "Utilisateur supprimé"}), 200

if __name__ == '__main__':
    app.run(debug=True, port=5000)