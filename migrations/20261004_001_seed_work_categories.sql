insert into public.work_types (code, name_en, name_ar, is_active)
values
    ('digital-art', 'Digital Art', 'فن رقمي', true),
    ('hand-art', 'Hand Art', 'فن يدوي', true),
    ('video', 'Video', 'فيديو', true),
    ('audio', 'Audio', 'صوت', true),
    ('animation', 'Animation', 'رسوم متحركة', true),
    ('games', 'Games', 'ألعاب', true),
    ('interactive', 'Interactive', 'تفاعلي', true),
    ('vr-ar', 'VR/AR', 'واقع افتراضي ومعزز', true)
on conflict (code) do update
set name_en = excluded.name_en,
    name_ar = excluded.name_ar,
    is_active = true;
