import { test } from '@playwright/test';
import Login from './login';
import Classification from './classification';
import Cadre from './cadre';
import jobType from './job_type';
import contactType from './contact_type';
import institutionType from './institution_type';
import grade from './grade';
import user from './user';

test.describe('User login', Login);
test.describe('classification', Classification);
test.describe('cadre', Cadre);
test.describe('job_type', jobType);
test.describe('contact_type', contactType);
test.describe('institution_type', institutionType);
test.describe('grade', grade);
test.describe('user', user);
