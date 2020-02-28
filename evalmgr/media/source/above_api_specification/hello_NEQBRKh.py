from flask import Flask
import requests
app = Flask(__name__)

@app.route('/hello')
def hello():
    r = requests.get('http://www.google.com')
    return r.text

if __name__ == '__main__':
	app.run()

	{
	"rideid":1000,
	"created_by":"r",
	"timestamp":"12-02-1987:57-32-12",
	"source":56,
	"destination":121
}