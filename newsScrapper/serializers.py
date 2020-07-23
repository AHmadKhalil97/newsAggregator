from rest_framework import serializers
from .models import Source, Headline

class HeadlineSerializer(serializers.ModelSerializer):
	class Meta:
		model = Headline
		fields = (
			'source', 'title', 'link'
		)

class SourceSerializer(serializers.ModelSerializer):
	news = HeadlineSerializer(many=True, read_only=True)
	class Meta:
		model = Source
		fields = ['source_name', 'source_link', 'source_category', 'updated_datetime', 'news']

# class CustomSerializer(serializers.Serializer):
# 	source = serializers.CharField()
# 	source_url = serializers.URLField()
# 	news_count = serializers.IntegerField()
# 	update_datetime = serializers.DateTimeField()
# 	news_list = serializers.ListField()