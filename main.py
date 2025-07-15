# creating my cafe api
from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Boolean
import random
from flask_wtf import FlaskForm
from wtforms import StringField , SubmitField
from wtforms.fields.choices import SelectField
from wtforms.validators import  DataRequired
from flask_bootstrap import Bootstrap5


app = Flask(__name__)

bootstrap = Bootstrap5(app)

# CREATE DB
class Base(DeclarativeBase):
    pass
# Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
db = SQLAlchemy(model_class=Base)
db.init_app(app)

app.secret_key = "jhdcbjchjchikdnbcjxhb"

# Cafe TABLE Configuration
class Cafe(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    map_url: Mapped[str] = mapped_column(String(500), nullable=False)
    img_url: Mapped[str] = mapped_column(String(500), nullable=False)
    location: Mapped[str] = mapped_column(String(250), nullable=False)
    seats: Mapped[str] = mapped_column(String(250), nullable=False)
    has_toilet: Mapped[bool] = mapped_column(Boolean, nullable=False)
    has_wifi: Mapped[bool] = mapped_column(Boolean, nullable=False)
    has_sockets: Mapped[bool] = mapped_column(Boolean, nullable=False)
    can_take_calls: Mapped[bool] = mapped_column(Boolean, nullable=False)
    coffee_price: Mapped[str] = mapped_column(String(250), nullable=True)

#creating a form add in my database
class Form(FlaskForm) :
    name = StringField('Name of the Cafe ', [DataRequired()])
    location = StringField('location of the cafe ' ,[DataRequired()] )
    map_url = StringField('map url of cafe ' , [DataRequired()])
    img_url = StringField('img url of cafe ' , [DataRequired()])
    seats = StringField('Seating capacity ',[DataRequired()])
    has_toilet = SelectField('does cafe has toilet ', choices=[('True' , 'Yes') , ('False' , 'No')] , coerce=lambda x : str(x).lower() == 'true', default='False')
    has_wifi = SelectField('does cafe has wifi ', choices=[('True' ,'Yes') , ('False' , 'No')] , coerce=lambda x : str(x).lower() == 'true')
    has_sockets = SelectField('does cafe has socket ' , choices=[('True' , 'Yes') , ('False' , 'No')] , coerce=lambda x : str(x).lower() == 'true')
    can_take_calls = SelectField('can customer take calls ' , choices=[('True' , 'Yes') , ('False' , 'No')] , coerce=lambda x : str(x).lower() == 'true' , default='False')
    coffee_price = StringField('price of the coffee' , [DataRequired()])
    submit = SubmitField('submit')



with app.app_context():
    db.create_all()
my_books = []

# this function will return a json file associated with a specific cafe
def return_json_database(cafe) :
    json_file = jsonify(cafe={
        "id": cafe.id,
        "name": cafe.name,
        "map_url": cafe.map_url,
        "img_url": cafe.img_url,
        "location": cafe.location,
        "seats": cafe.seats,
        "has_toilet": cafe.has_toilet,
        "has_wifi": cafe.has_wifi,
        "has_sockets": cafe.has_sockets,
        "can_take_calls": cafe.can_take_calls,
        "coffee_price": cafe.coffee_price,
    })
    return json_file

# creating an error json  with custom message
def error(error_code,response) :
    json_file = jsonify(error={'error code' : error_code , 'response ' : response})
    return json_file , error_code


def string_to_bool(value) :
    return str(value).lower() == 'true'

# home
@app.route("/")
def home():
    return render_template("index.html")



# get all cafe's in database
@app.route("/all", methods=['GET'])
def all() :
    cafes = []
    result = db.session.execute(db.select(Cafe).order_by(Cafe.name))
    all_cafes = result.scalars().all()

    for cafe in all_cafes :
        cafes.append({
                 "id" :  cafe.id,
                 "name": cafe.name,
                 "map_url": cafe.map_url,
                 "img_url": cafe.img_url,
                 "location": cafe.location ,
                 "seats": cafe.seats,
                 "has_toilet": cafe.has_toilet,
                 "has_wifi": cafe.has_wifi,
                 "has_sockets": cafe.has_sockets,
                 "can_take_calls": cafe.can_take_calls,
                 "coffee_price": cafe.coffee_price,
             })

    new_dict = jsonify(cafes=cafes)
    return new_dict


@app.route("/random_cafe" , methods=['GET'])
def random_cafe():
    result = db.session.execute(db.select(Cafe).order_by(Cafe.name))
    all_cafes = result.scalars().all()
    # random cafe
    cafe_ = random.choice(all_cafes)
    return return_json_database(cafe_)


# function to search any cafe in my database
@app.route("/search" , methods=['GET'])
def search() :
    try :
        location = request.args.get('location')

        my_result = db.session.execute(db.select(Cafe).order_by(Cafe.name))
        list_of_all_cafes = my_result.scalars().all()

        founded_cafes = []

        for cafe in list_of_all_cafes:
            if cafe.location == location:
                founded_cafes.append(cafe)

        # storing founded cafe's in json format
        founded_cafe_json = []
        for cafe in founded_cafes:
            founded_cafe_json.append({
                "id": cafe.id,
                "name": cafe.name,
                "map_url": cafe.map_url,
                "img_url": cafe.img_url,
                "location": cafe.location,
                "seats": cafe.seats,
                "has_toilet": cafe.has_toilet,
                "has_wifi": cafe.has_wifi,
                "has_sockets": cafe.has_sockets,
                "can_take_calls": cafe.can_take_calls,
                "coffee_price": cafe.coffee_price,

            })

        new_dict = jsonify(cafes=founded_cafe_json)
        if len(founded_cafe_json) > 0:
            return new_dict
        else:
            return error(404, 'no cafe found at this location')
    except  SQLAlchemyError:
        return error(500 , 'error occur while searching ')

#add a cafe in the database
@app.route("/add_cafe" , methods=['POST'])
def add_cafe() :
    cafe_name = request.form.get('name')
    map_url= request.form.get('map_url')
    img_url= request.form.get('img_url')
    location= request.form.get('location')
    seats= request.form.get('seats')
    coffee_price=request.form.get('coffee_price')

    has_toilet = string_to_bool(request.form.get('has_toilet'))
    has_wifi = string_to_bool(request.form.get('has_wifi'))
    has_sockets = string_to_bool(request.form.get('has_sockets'))
    can_take_calls = string_to_bool(request.form.get('can_take_calls'))


    try :
        cafe = Cafe(
                name=cafe_name,
                map_url=map_url,
                img_url=img_url,
                location=location,
                seats=seats,
                has_toilet=has_toilet,
                has_wifi=has_wifi,
                has_sockets=has_sockets,
                can_take_calls=can_take_calls,
                coffee_price=coffee_price,
            )
        db.session.add(cafe)
        db.session.commit()
        return return_json_database(cafe)


    except IntegrityError :
        return error(409 , 'cafe already exists ')


    except SQLAlchemyError :
        return error(500 ,'unable to add cafe in the database ')





# function to add a cafe in my database in gui format
@app.route("/add_cafe_form" , methods=["POST"])
def add_cafe_form() :
    form = Form()
    if form.validate_on_submit() :
        with app.app_context() :
            new_entry = Cafe(
                name=form.name.data  ,
                map_url=form.map_url.data ,
                img_url=form.img_url.data  ,
                location=form.location.data ,
                seats=form.seats.data  ,
                has_toilet=form.has_toilet.data ,
                has_wifi=form.has_wifi.data  ,
                has_sockets=form.has_sockets.data,
                can_take_calls=form.can_take_calls.data ,
                coffee_price=form.coffee_price.data ,
            )
            db.session.add(new_entry)
            db.session.commit()


            cafe_  = db.session.execute(db.select(Cafe).where(Cafe.name == form.name.data )).scalar()
            # adding this cafe to the database
            return return_json_database(cafe_)
    return render_template('add.html',form=form)


# get any cafe by id
@app.route('/cafe/<int:id>' , methods=['GET'])
def cafe(id) :
    try :
        cafe_ = db.session.execute(db.select(Cafe).where(Cafe.id == id)).scalar()
        return  return_json_database(cafe_)
    except SQLAlchemyError :
        return error(404 , f'could not find cafe with id : {id}')

# delete any cafe by id
@app.route("/delete" , methods=['DELETE'])
def delete() :
    id = request.args.get('id')
    try :
        id = int(id)
        cafe_to_delete = db.session.execute(db.select(Cafe).where(Cafe.id == id)).scalar()
        if cafe_to_delete is None :
            return  jsonify(error={'deletion fail' : 'cannot delete null '})
        else :
            db.session.delete(cafe_to_delete)
            db.session.commit()
            return jsonify(succes={'delete successful': f'cafe with id : {id} removed from the database'})
    except SQLAlchemyError :
        json_file = jsonify(error={'failed' : f'unable to delete cafe with {id} in the database '})
        return  json_file , 500
    except (TypeError ,ValueError ) :
        return jsonify(error = {'deletion failed' : 'unable to process id ' }) , 500




@app.route("/cafe/update_price", methods=['PATCH'])
def update_price() :
    id = int(request.args.get('id'))
    new_price = request.args.get('price')
    if new_price != None :
        with app.app_context() :
            cafe_to_update = db.session.execute(db.select(Cafe).where(Cafe.id == id)).scalar()
            cafe_to_update.coffee_price = new_price
            db.session.commit()

            json_file = jsonify(error={"success": "price updated successfully"})
            return json_file
    else :
        return error(500 , "cannot change price , something went wrong ")


if __name__ == '__main__':
    app.run(debug=True)

