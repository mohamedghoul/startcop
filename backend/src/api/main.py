from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/')
def health():
    return "StartCop: The AI Powered Regulatory Navigator API"

if __name__ == '__main__':
    app.run(debug=True)