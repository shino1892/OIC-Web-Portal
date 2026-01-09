-- FK for timetable sync config (runs after 999_* seed scripts due to filename order)
ALTER TABLE department_spreadsheets
    ADD CONSTRAINT fk_department_spreadsheets_department FOREIGN KEY (department_id) REFERENCES departments(id);

ALTER TABLE major_aliases
    ADD CONSTRAINT fk_major_aliases_department FOREIGN KEY (department_id) REFERENCES departments(id);
