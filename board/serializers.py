from rest_framework import serializers
from .models import Sprint,Task
from django.contrib.auth import get_user_model
from rest_framework.reverse import reverse	
from datetime import date
from django.utils.translation import gettext_lazy as _

User = get_user_model()

class SprintSerializer(serializers.ModelSerializer):

	links = serializers.SerializerMethodField()

	class Meta:
		model = Sprint
		fields = ('id','name','description','end','links')

	def get_links(self , obj):
		request = self.context['request']
		return {
			'self': reverse('sprint-detail', kwargs={'pk': obj.pk}, request=request),
			'tasks': reverse('task-list',request=request)+'?sprint={}'.format(obj.pk),
		}

	def validate_end(self, value ):
		new = not self.instance 
		changed = (self.instance and self.instance.end != value )
		if (new or changed ) and value < date.today() :
			msg = _("Bawla hai kya !!!")
			raise serializers.ValidationError(msg)
		return value

class TaskSerializer(serializers.ModelSerializer):

	assigned = serializers.SlugRelatedField(slug_field=User.USERNAME_FIELD, required=False,read_only=True)
	status_display = serializers.SerializerMethodField()
	links = serializers.SerializerMethodField()
	
	class Meta:
		model = Task
		fields = ['id', 'name', 'description', 'sprint', 'status','status_display', 'order',
			'assigned', 'started', 'due', 'completed','links' ,]

	def get_status_display(self, obj):
		return obj.get_status_display()
		
	def get_links(self , obj):
		request = self.context['request']
		links = {
			'self' : reverse ('task-detail', kwargs={ 'pk' : obj.pk}, request=request),
			'assigned' : None ,
			'sprint' :None ,
		}
		if obj.sprint_id:
			links['sprint'] = reverse('sprint-detail',
				kwargs={'pk': obj.sprint_id}, request=request)
		if obj.assigned:
			links['assigned'] = reverse('user-detail',
				kwargs={User.USERNAME_FIELD: obj.assigned}, request=request)
		return links

	def validate_sprint(self,value ):
		if self.instance and not self.instance.pk :
			print("Going Crazy!!!")

		if not Sprint.objects.filter(name=value) :
			raise serializers.ValidationError(_("Sprint does not exist"))

		if self.instance and self.instance.pk :
			if 	value!= self.instance.sprint:
				if value and value.end < date.today() :
					raise serializers.ValidationError(_("Can't assign tasks for completed sprints."))
				if self.instance.status == Task.STATUS_DONE :
					raise serializers.ValidationError(_("Cannot change the sprint of a completed event."))
		else:
			if value and value.end < date.today():
				raise serializers.ValidationError(
					_("Can't assign tasks for completed sprints."))
		return value 

	def validate(self,attrs):
		sprint = attrs.get('sprint')
		status = attrs.get('status')
		started = attrs.get('started')
		completed = attrs.get('completed')
		if not sprint and status != Task.STATUS_TODO:
			msg = _('Backlog tasks must have "Not Started" status.')
			raise serializers.ValidationError(msg)
		if started and status == Task.STATUS_TODO:
			msg = _('Started date cannot be set for not started tasks.')
			raise serializers.ValidationError(msg)
		if completed and status != Task.STATUS_DONE:
			msg = _('Completed date cannot be set for uncompleted tasks.')
			raise serializers.ValidationError(msg)
		return attrs

class UserSerializer(serializers.ModelSerializer):

	full_name = serializers.CharField(source='get_full_name',read_only=True)
	links = serializers.SerializerMethodField()

	class Meta:
		model = User
		fields = ['id',User.USERNAME_FIELD , 'full_name','is_active','links',]

	def get_links(self , obj):
		request = self.context['request']
		username = obj.get_username()
		print(obj.pk)
		return {
			'self' : reverse('user-detail',kwargs={User.USERNAME_FIELD : username}, request=request),
			'tasks': reverse('task-list', request=request)+'?assigned={}'.format(username), 
		}
