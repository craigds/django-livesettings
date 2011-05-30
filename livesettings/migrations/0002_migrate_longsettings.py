# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        # Changing field 'Setting.value'
        db.alter_column('livesettings_setting', 'value', self.gf('django.db.models.fields.TextField')())
        
        # turn longsettings into settings
        for s in orm['livesettings.longsetting'].objects.all():
            orm['livesettings.setting'].objects.filter(site__id=s.site_id, group=s.group, key=s.key).delete()
            orm['livesettings.setting'].objects.create(
                site_id=s.site_id,
                group=s.group,
                key=s.key,
                value=s.value
            )

    def backwards(self, orm):
        for s in orm['livesettings.setting'].objects.all():
            if len(s.value) > 255:
                s.delete()
        
        # Changing field 'Setting.value'
        db.alter_column('livesettings_setting', 'value', self.gf('django.db.models.fields.CharField')(max_length=255))


    models = {
        'livesettings.longsetting': {
            'Meta': {'unique_together': "(('site', 'group', 'key'),)", 'object_name': 'LongSetting'},
            'group': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'key': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'site': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sites.Site']"}),
            'value': ('django.db.models.fields.TextField', [], {'blank': 'True'})
        },
        'livesettings.setting': {
            'Meta': {'unique_together': "(('site', 'group', 'key'),)", 'object_name': 'Setting'},
            'group': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'key': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'site': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sites.Site']"}),
            'value': ('django.db.models.fields.TextField', [], {'blank': 'True'})
        },
        'sites.site': {
            'Meta': {'ordering': "('domain',)", 'object_name': 'Site', 'db_table': "'django_site'"},
            'domain': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        }
    }

    complete_apps = ['livesettings']
