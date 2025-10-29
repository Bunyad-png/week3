# from pydantic import BaseModel, EmailStr

# class UserCreate(BaseModel):
#     first_name: str
#     last_name: str
#     email: EmailStr
#     password: str
#     username: str

# class UserResponse(BaseModel):
#     email: EmailStr
#     is_active: bool

#     class Config:
#         from_attributes = True

# class LoginRequest(BaseModel):
#     identifier: str
#     password: str


# class ResetPasswordRequest(BaseModel):
#     username: str
#     code: int
#     new_pass: str

# class UserResponss(BaseModel):
#     id: int
#     first_name: str
#     last_name: str
#     email: EmailStr
#     username: str
#     followers: int
#     followings: int
#     user_img: str


# class UserWithFollowResponse(BaseModel):
#     first_name: str
#     last_name: str
#     email: EmailStr
#     username: str
#     followers: int
#     followings: int
#     user_img: str
#     has_followed: bool

# class LoginResponse(BaseModel):
#     message: str
#     access_token: str
#     refresh_token: str
#     token_type: str

#     class Config:
#         from_attributes = True

# class Token(BaseModel):
#     access_token: str
#     token_type: str


#     class Config:
#         from_attributes = True




from pydantic import BaseModel, EmailStr,  Field
from datetime import datetime

class UserCreate(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    password: str
    username: str

class UserSearchOut(BaseModel):
    username: str
    user_img: str | None
    has_followed: bool

class PostDetail(BaseModel):
    id: int
    image: str
    username: str
    user_image: str
    text: str
    has_liked: bool
    has_followed: bool
    likes: int
    comments: int

class CommentOut(BaseModel):
    id: int
    content: str
    this_user: bool
    created_at: datetime
    username: str
    user_img: str | None
    has_followed: bool


class CommentCreate(BaseModel):
    content: str = Field(..., min_length=1)
    post_id: int

# Модель для ответа
class CommentResponse(BaseModel):
    message: str

class FollowRequest(BaseModel):
    username: str

class UnfollowRequest(BaseModel):
    username: str
    
class LikeRequest(BaseModel):
    post_id: int

class PostOut(BaseModel):
    id: int
    text: str
    image_id: int
    created_at: datetime


class Postcreate(BaseModel):
    text: str
    image_id: int

class UserResponse(BaseModel):
    email: EmailStr
    is_active: bool

    class Config:
        orm_mode = True  # исправлено с from_attributes на orm_mode

class LoginRequest(BaseModel):
    identifier: str
    password: str

class ResetPasswordRequest(BaseModel):
    username: str
    code: int
    new_pass: str

class UserResponss(BaseModel):
    id: int
    first_name: str
    last_name: str
    email: EmailStr
    username: str
    followers: int
    followings: int
    user_img: str

    class Config:
        orm_mode = True  # добавлено

class UserWithFollowResponse(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    username: str
    followers: int
    followings: int
    user_img: str
    has_followed: bool



    class Config:
        orm_mode = True  # добавлено

class LoginResponse(BaseModel):
    message: str
    access_token: str
    refresh_token: str
    token_type: str

    class Config:
        orm_mode = True  # исправлено

class Token(BaseModel):
    access_token: str
    token_type: str

    class Config:
        orm_mode = True  # исправлено
