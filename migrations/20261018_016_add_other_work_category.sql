insert into public.work_types (code, name_en, name_ar, is_active)
values ('other', 'Other', 'أخرى', true)
on conflict (code) do update
set name_en = excluded.name_en,
    name_ar = excluded.name_ar,
    is_active = true;
