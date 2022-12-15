from flask import Blueprint,jsonify,request
from flask_jwt_extended import jwt_required,get_jwt_identity
import validators
from .database import db,Bookmark
from .constants.http_status_code import HTTP_400_BAD_REQUEST,HTTP_409_CONFLICT,HTTP_500_INTERNAL_SERVER_ERROR,HTTP_201_CREATED,HTTP_200_OK

bookmarks = Blueprint("bookmarks",__name__,url_prefix="/api/bookmarks")

# get all of my bookmarks
@bookmarks.get("/")
@jwt_required()
def index():
    user_id = get_jwt_identity()

    # we gonna implement pagination here.
    page = request.args.get("page",1,type=int)
    per_page = request.args.get("per_page",5,type=int)

    # get bookmarks 
    bookmarks = Bookmark.query.filter_by(user_id=user_id).paginate(page=page,per_page=per_page)

    data = []

    for bookmark in bookmarks:
        data.append({
            "id":bookmark.id,
            "body":bookmark.body,
            "url":bookmark.url,
            "short_url":bookmark.short_url,
            "visits":bookmark.visits,
            "created_at":bookmark.created_at,
            "updated_at":bookmark.updated_at
        })
    
    # important meta data for pagination
    meta = {
        "page":bookmarks.page,
        "pages":bookmarks.pages,
        "total_items":bookmarks.total,
        "prev_page":bookmarks.prev_num,
        "next_page":bookmarks.next_num,
        "has_next":bookmarks.has_next,
        "has_prev":bookmarks.has_prev
    }    

    return jsonify({"data":data,"meta":meta}) , HTTP_200_OK


# create new bookmark
@bookmarks.post("/")
@jwt_required()
def addBookmark():
    user_id=get_jwt_identity()
    body = request.json.get("body","")
    url = request.json.get("url","")

    # see if not url is valid
    if not validators.url(url):
        return jsonify({
           "msg":"Url is not valid"
        }), HTTP_400_BAD_REQUEST

    # see if the url already exits 
    if Bookmark.query.filter_by(url=url).first():
         return jsonify({
           "msg":"Url is not valid"
         }), HTTP_409_CONFLICT 
    
    # if everything is ok then we will create a new bookmark
    newBookmark=Bookmark(body=body,url=url,user_id=user_id)
    try:
        db.session.add(newBookmark)
        db.session.commit()

        return jsonify({
            "id":newBookmark.id,
            "body":newBookmark.body,
            "url":newBookmark.url,
            "short_url":newBookmark.short_url,
            "visits":newBookmark.visits,
            "created_at":newBookmark.created_at,
            "updated_at":newBookmark.updated_at
        }) , HTTP_201_CREATED
    except:
         return jsonify({
           "msg":"Interval server errror."
         }), HTTP_500_INTERNAL_SERVER_ERROR


