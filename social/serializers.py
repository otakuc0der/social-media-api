from rest_framework import serializers

from social.models import Comment, Hashtag, Post


class HashtagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Hashtag
        fields = [
            "id",
            "name",
        ]


class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = [
            "id",
            "content",
            "image",
            "hashtags",
        ]


class PostListSerializer(PostSerializer):
    author = serializers.CharField(
        source="author.profile.nickname",
        read_only=True,
    )
    hashtags = serializers.SlugRelatedField(
        many=True,
        read_only=True,
        slug_field="name",
    )

    class Meta(PostSerializer.Meta):
        fields = PostSerializer.Meta.fields + [
            "status",
            "author",
            "created_at",
        ]


class PostDetailSerializer(PostSerializer):
    author = serializers.CharField(
        source="author.profile.nickname",
        read_only=True,
    )
    hashtags = HashtagSerializer(
        many=True,
        read_only=True,
    )

    class Meta(PostSerializer.Meta):
        fields = PostSerializer.Meta.fields + [
            "status",
            "author",
            "created_at",
            "updated_at",
        ]


class EmptySerializer(serializers.Serializer):
    pass


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = [
            "content",
        ]


class CommentListSerializer(CommentSerializer):
    author = serializers.CharField(
        source="author.profile.nickname",
        read_only=True,
    )
    post = serializers.UUIDField(
        source="post.pk",
        read_only=True,
    )

    class Meta(CommentSerializer.Meta):
        fields = [
            "id",
            "author",
            "content",
            "post",
            "created_at",
        ]


class CommentDetailSerializer(CommentSerializer):
    author = serializers.CharField(
        source="author.profile.nickname",
        read_only=True,
    )
    post = serializers.UUIDField(
        source="post.pk",
        read_only=True,
    )

    class Meta(CommentSerializer.Meta):
        fields = [
            "id",
            "author",
            "content",
            "post",
            "created_at",
            "updated_at",
        ]
