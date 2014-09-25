import web
import json

urls = ("/.*", "index")
app = web.application(urls, globals())
#content = {"key1": "value1", "key2": "value2"};
content = {}

class index:

    def GET(self):
			web.header('Access-Control-Allow-Origin',      '*')
			web.header('Content-Type', 'application/json')
			content = {}
			content = get_data()
			return json.dumps(content)
			#return content
		
def get_data():
		fp = open("C:\Python27\displayCluster.json","r")
		return json.load(fp)	
	
if __name__ == "__main__":
    app.run()