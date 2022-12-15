from flask import Blueprint,jsonify,request
from werkzeug.security import check_password_hash,generate_password_hash
from flask_jwt_extended import create_access_token,create_refresh_token,jwt_required,get_jwt_identity
from .database import db,User
import validators
from .constants.http_status_code import HTTP_400_BAD_REQUEST,HTTP_409_CONFLICT,HTTP_500_INTERNAL_SERVER_ERROR,HTTP_201_CREATED , HTTP_200_OK , HTTP_401_UNAUTHORIZED

auth = Blueprint("auth",__name__,url_prefix="/api/auth")

# Route to handle user register
@auth.post("/register")
def register():
    name = request.json.get("name","")
    email = request.json.get("email","")
    password = request.json.get("password","")

    # check validation
    if ((len(name) < 3) or (not validators.email(email)) or (len(password) < 3)):
        return jsonify({"msg":"please provide all the info correctly."}) , HTTP_400_BAD_REQUEST

    # see if email alrady taken
    if  User.query.filter_by(email=email).first() is not None:
        return jsonify({"msg":"Email taken"}) , HTTP_409_CONFLICT

    # if everything is ok
    hashPass = generate_password_hash(password)  
    newUser = User(name=name,email=email,password=hashPass)

    try:
        db.session.add(newUser)
        db.session.commit()
        # genarate refresh and access token for the user with id
        refreshToken=create_refresh_token(identity=newUser.id)
        accessToken=create_access_token(identity=newUser.id)

        return jsonify({
            "msg":"user created login to continue.",
            "user":{
                "name":name,
                "email":email,
                "accessToken":accessToken,
                "refreshToken":refreshToken
            }
        }) , HTTP_201_CREATED
    except:
        return jsonify({"msg":"Server error"}) , HTTP_500_INTERNAL_SERVER_ERROR


# Route to handle user login
@auth.post("/login")
def login():
    email = request.json.get("email","")
    password = request.json.get("password","")

    # see if email is correct
    user = User.query.filter_by(email=email).first()
    if user:
        # check if password match
        if check_password_hash(user.password,password):
            # everything is ok
            # genarate refresh and access token for the user with id
            refreshToken=create_refresh_token(identity=user.id)
            accessToken=create_access_token(identity=user.id)

            return jsonify({
                "msg":"login successful",
                "user":{
                    "name":user.name,
                    "email":user.email,
                    "accessToken":accessToken,
                    "refreshToken":refreshToken
                }
            }) , HTTP_200_OK

    # if not user found / pass dont match
    return jsonify({
        "msg":"Wrong Creds!!"
    }) , HTTP_401_UNAUTHORIZED       


# get my info(if my token is valid and correct)
@auth.get("/me")
@jwt_required()
def serveProfile():
    my_id=get_jwt_identity()

    user = User.query.filter_by(id=my_id).first()

    return jsonify({
        "name":user.name,
        "email":user.email
    }) , HTTP_200_OK


# create a new access token for user if its expired using refresh token
@auth.get("/token/refresh")
@jwt_required()
def refreshUserToken():
    user_id=get_jwt_identity()
    accessToken=create_access_token(identity=user_id)

    return jsonify({
        "msg":"new access token created",
        "accessToken":accessToken
    }),HTTP_200_OK    

