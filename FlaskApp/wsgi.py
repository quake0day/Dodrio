from main import app
from werkzeug.serving import run_simple
if __name__ == "__main__":
	context = ('4fa581949f17aaa.crt', 'darlingtree.key')
	#app.run(host='0.0.0.0', port=443, ssl=context, DEBUG=True)
	run_simple('0.0.0.0', 443, app, ssl_context=('./4fa581949f17aaa.crt', 'darlingtree.key'))
