# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Setting'
        db.create_table('livesettings_setting', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('site', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['sites.Site'])),
            ('group', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('key', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('value', self.gf('django.db.models.fields.CharField')(max_length=255, blank=True)),
        ))
        db.send_create_signal('livesettings', ['Setting'])

        # Adding unique constraint on 'Setting', fields ['site', 'group', 'key']
        db.create_unique('livesettings_setting', ['site_id', 'group', 'key'])

        # Adding model 'LongSetting'
        db.create_table('livesettings_longsetting', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('site', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['sites.Site'])),
            ('group', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('key', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('value', self.gf('django.db.models.fields.TextField')(blank=True)),
        ))
        db.send_create_signal('livesettings', ['LongSetting'])

        # Adding unique constraint on 'LongSetting', fields ['site', 'group', 'key']
        db.create_unique('livesettings_longsetting', ['site_id', 'group', 'key'])


    def backwards(self, orm):
        
        # Removing unique constraint on 'LongSetting', fields ['site', 'group', 'key']
        db.delete_unique('livesettings_longsetting', ['site_id', 'group', 'key'])

        # Removing unique constraint on 'Setting', fields ['site', 'group', 'key']
        db.delete_unique('livesettings_setting', ['site_id', 'group', 'key'])

        # Deleting model 'Setting'
        db.delete_table('livesettings_setting')

        # Deleting model 'LongSetting'
        db.delete_table('livesettings_longsetting')


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
            'value': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'})
        },
        'sites.site': {
            'Meta': {'ordering': "('domain',)", 'object_name': 'Site', 'db_table': "'django_site'"},
            'domain': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        }
    }

    complete_apps = ['livesettings']
