"""Source settings audit. Never invent playlist/song members absent from captures."""
import math

FIELDS={'loop':('loop','repeat'),'fade':('fade','fadeIn','fadeOut'),'channel':('channel','type'),'mode':('mode',)}
def settings(source, identity, losses):
    result={}
    for field,keys in FIELDS.items():
        value={k:source[k] for k in keys if k in source}
        result[field]={'status':'manual','source':value,'native_field':None}
        losses.append({'grade':'manual','feature':'playlist-'+field,'source_id':identity,'source_setting':value,
            'summary':'Captured user/shipped playlist/song records have no demonstrated '+field+' control; configure it manually. Unspecified source values are not inferred.'})
    value=source.get('volume')
    valid=type(value) in (int,float) and math.isfinite(value) and 0<=value<=1
    result['volume']={'source':value,'status':'approximate' if valid else 'default' if value is None else 'manual','native_field':'MusicTrackInfo._trackVolumes[Master]'}
    return result

def gain(value, losses, identity):
    if value is None:return None
    if type(value) not in (int,float) or not math.isfinite(value) or not 0<=value<=1:
        losses.append({'grade':'manual','feature':'playlist-volume','source_id':identity,'source_value':value,'summary':'Invalid/out-of-range volume factor ignored; Master 0.8 retained only if neither valid factor is available'})
        return None
    losses.append({'grade':'approximate','feature':'playlist-volume','source_id':identity,'source_value':value,'native_field':'MusicTrackInfo._trackVolumes[Master]',
        'summary':'Normalized gain mapped; playlist/track gains multiply where both supplied. Source loudness curve and native acoustic equivalence unverified.'})
    return float(value)
