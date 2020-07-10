import os, re
from flask import Flask, render_template, redirect, request, url_for, send_from_directory
from flask_pymongo import PyMongo
from bson.objectid import ObjectId


app = Flask(__name__)

#link database to application
app.config["MONGO_DBNAME"] = 'cocktailHandbook'
app.config["MONGO_URI"] = 'mongodb+srv://root:excellent0909@cluster0-dxqrw.mongodb.net/cocktailHandbook?retryWrites=true&w=majority'
APP_ROOT = os.path.dirname(os.path.abspath(__file__))

#instance of PyMongo
mongo = PyMongo(app)

#connection to database default function
@app.route('/')
@app.route('/get_cocktails')
def get_cocktails():
    return render_template("cocktails.html", cocktails=mongo.db.cocktails.find())

    
#display cocktails from searchbar
@app.route('/search_cocktails', methods=["GET", "POST"])
def search_cocktails():
    if request.method == "POST":
        req = request.form
        search_form = req.get('search_field') 
        #search_fields = {"cocktail_name" : search_form}
        search_form_re = re.compile('.*(%s).*'%search_form, flags= re.I)
        #search_fields = {"cocktail_name" : search_form}
        search_fields = {"cocktail_name" : search_form_re}
        return render_template("cocktails.html", cocktails=mongo.db.cocktails.find(search_fields))

#display addCocktail page 
@app.route('/add_cocktail')
def add_cocktail():
    return render_template("addCocktail.html", 
    glasses=mongo.db.glass.find())
    
#add new cocktail button functionality  
@app.route('/insert_cocktail', methods=['POST'])
def insert_cocktail():
    target = os.path.join(APP_ROOT, 'static/images/cocktails')
    print(target)
    
    if not os.path.isdir(target):
        os.mkdir(target)
        
    for file in request.files.getlist("cocktail_image"):
        print(file)
        filename = file.filename
        destination = "/".join([target, filename])
        print("file is loacated" + destination)
        file.save(destination)
        
    cocktails = mongo.db.cocktails
    
    form_data = {
        'cocktail_name' : request.form.get('cocktail_name'),
        'glass_name' : request.form.get('glass_name'),
        'cocktail_description' : request.form.get('cocktail_description'),
        'preparation_steps' : request.form.get('preparation_steps'),
        'is_virgin' : request.form.get('is_virgin'),
        'ingredients' : request.form.get('ingredients'),
        'cocktail_strength' : request.form.get('cocktail_strength'),
        'cocktail_image' : destination
    }
    
    #cocktails.insert_one(request.form.to_dict())
    cocktails.insert_one(form_data)
    
    return render_template("cocktails.html", cocktails=mongo.db.cocktails.find(), image_name=filename)
    #return redirect(url_for('get_cocktails'), image_name=filename)
 
#retrieve image path for cocktail images
@app.route('/upload/<filename>')
def send_image(filename):
    return send_from_directory("static/images/cocktails", filename)
    
#edit button functionality
@app.route('/edit_cocktail/<cocktail_id>')
def edit_cocktail(cocktail_id):
    the_cocktail = mongo.db.cocktails.find_one({"_id": ObjectId(cocktail_id)})
    all_categories = mongo.db.categories.find()
    return render_template('editCocktail.html', cocktail = the_cocktail, categories = all_categories)
    
@app.route('/update_cocktail/<cocktail_id>', methods=["POST"])
def update_cocktail(cocktail_id):
    cocktail = mongo.db.cocktails
    cocktail.update_cocktail( {'_id': ObjectId(cocktail_id)},
       { 
        'cocktail_name' : request.form.get['cocktail_name'],
        'glass_name' : request.form.get['glass_name'],
        'cocktail_description' : request.form.get['cocktail_description'],
        'preparation_steps' : request.form.get['preparation_steps'],
        'is_virgin' : request.form.get['is_virgin']
        })
    return redirect(url_for('get_cocktails'))

@app.route('/delete_cocktail/<cocktail_id>')
def delete_cocktail(cocktail_id):
    mongo.db.cocktails.remove({'_id': ObjectId(cocktail_id)})
    return redirect(url_for('get_cocktails'))

@app.route('/get_glasses')
def get_glasses():
    return render_template('glasses.html', 
    glasses=mongo.db.glass.find())
    
@app.route('/edit_glasses/<glass_id>')
def edit_glass(glass_id):
    return render_template('editglass.html',
    glass = mongo.db.glass.find_one({'_id': ObjectId(glass_id)}))
   
@app.route('/update_glass/<glass_id>', methods=["POST"])
def update_glass(glass_id):
    mongo.db.glass.update(
        {'_id' : ObjectId(glass_id)},
        {'glass_name': request.form.get('glass_name')})
    return redirect(url_for('get_glasses'))
    
@app.route('/delete_glass/<glass_id>')
def delete_glass(glass_id):
    mongo.db.glass.remove({'_id' : ObjectId(glass_id)})
    return redirect(url_for('get_glasses'))
    
@app.route('/insert_glass', methods=["POST"])
def insert_glass():
    glasses = mongo.db.glass
    glass_doc = {'glass_name': request.form.get('glass_name')}
    glasses.insert_one(glass_doc)
    return redirect(url_for('get_glasses'))
    
@app.route("/add_glass")
def add_glass():
    return render_template('addglass.html')
    
    
if __name__ == '__main__':
    app.run(host = os.environ.get('IP'),
    port=int(os.environ.get('PORT')),
    debug=True)

