# yourapp/serializers.py
from rest_framework import serializers
from .models import User, FriendRequest
from django.contrib.auth.hashers import make_password, check_password

class SignUpSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)


    def create(self, validated_data):
        validated_data['password'] = make_password(validated_data['password'])
        validated_data['username'] = validated_data['username'] if validated_data.get('username') else validated_data['email']
        validated_data['email'] = validated_data['email'].lower()
        user = User.objects.create(**validated_data)
        return user



# yourapp/serializers.py
from rest_framework import serializers
from django.contrib.auth import authenticate

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)




    def validate(self, data):
        email = data.get('email')
        password = data.get('password')

        user = User.objects.filter(email__iexact=email).first()

        if not user:
            raise serializers.ValidationError("Incorrect credentials. Please try again.")
        
        if not check_password(password, user.password):
            raise serializers.ValidationError("Incorrect credentials. Please try again.")

        data['user'] = user
        return data
    
# serializers.py
from rest_framework import serializers
from .models import User

class UserSearchSerializer(serializers.Serializer):
    email = serializers.CharField(required=False)
    name = serializers.CharField(required=False)

    def validate(self, data):
        if not data.get('email') and not data.get('name'):
             raise serializers.ValidationError("Please provide search param.")
        
        return data


    def validate_email(self, value):
        # You can add custom validation logic here if needed
        return value

    def validate_name(self, value):
        # You can add custom validation logic here if needed
        return value

class FriendRequestSerializer(serializers.Serializer):
    id = serializers.IntegerField()

    def validate(self, data):
        if not data["id"]:
            raise serializers.ValidationError("Please provide friend request param.")
        
        return data
    
class SendFriendRequestSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()

    def validate(self, data):
        if not data["user_id"]:
            raise serializers.ValidationError("Please provide friend id as request param.")
        
        return data
    
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username']

class ListFriendRequestSerializer(serializers.ModelSerializer):
    to_user = UserSerializer()

    class Meta:
        model = FriendRequest
        fields = ['id', 'from_user', 'request_status']

    

