<script>
import { defineComponent } from 'vue';
import PeopleService from './people.service';
import NotifyService from '@/service/Notify.service';
import ConfirmModal from '@/components/ConfirmModal.vue';
import RoleService from '../role/roleService';
import constants from '../../../../service/constants';

export default defineComponent({
    name: 'PeopleDuplicates',
    components: {
        ConfirmModal
    },
    data() {
        return {
            loading: false,
            allowed: false,
            checkingAccess: true,
            groups: [],
            pendingDelete: null,
            displayConfirm: false
        };
    },
    async created() {
        this.allowed = await RoleService.userHasAction(constants.ACTIONS.CAN_DELETE_DUPLICATE_PERSON);
        this.checkingAccess = false;
        if (this.allowed) {
            this.loadDuplicates();
        }
    },
    methods: {
        loadDuplicates() {
            this.loading = true;
            PeopleService.duplicates()
                .then((groups) => {
                    this.groups = groups;
                })
                .catch((error) => {
                    console.error('Error fetching duplicate people:', error);
                    NotifyService.danger(this, '', null);
                })
                .finally(() => {
                    this.loading = false;
                });
        },
        gotoView(id) {
            this.$router.push(`/manage/people_record_view?id=${id}`);
        },
        askDelete(person) {
            this.pendingDelete = person;
            this.displayConfirm = true;
        },
        closeConfirm(result) {
            this.displayConfirm = false;
            if (!result || !this.pendingDelete) {
                this.pendingDelete = null;
                return;
            }

            const person = this.pendingDelete;
            this.pendingDelete = null;

            PeopleService.delete(person.id)
                .then(() => {
                    NotifyService.success(this, '', null);
                    this.loadDuplicates();
                })
                .catch(() => {
                    NotifyService.danger(this, '', null);
                });
        }
    }
});
</script>

<template>
    <div class="card manage-container">
        <h4>{{ $t('TREE.PEOPLE_DUPLICATES') }}</h4>

        <div v-if="checkingAccess"></div>
        <div v-else-if="!allowed" class="empty-state">
            <i class="pi pi-lock text-2xl"></i>
            <span>{{ $t('FORM.INFO.USER_PAGE_PERMISSION') }}</span>
        </div>

        <template v-else>
            <p class="text-600">{{ $t('FORM.LABELS.PEOPLE_DUPLICATES_HINT') }}</p>
            <hr />

            <div v-if="loading" class="text-600">{{ $t('FORM.LABELS.LOADING') }}</div>

        <div v-else-if="groups.length === 0" class="empty-state">
            <i class="pi pi-check-circle text-green-500 text-2xl"></i>
            <span>{{ $t('FORM.LABELS.NO_DUPLICATES_FOUND') }}</span>
        </div>

        <div v-else class="duplicate-group" v-for="(group, index) in groups" :key="index">
            <div class="duplicate-group-header">
                {{ group[0].lastname }} {{ group[0].firstname }} <span v-if="group[0].middlename">{{ group[0].middlename }}</span>
                &mdash; {{ group[0].birthdate }}
            </div>

            <div class="duplicate-candidate" v-for="person in group" :key="person.id">
                <div class="duplicate-candidate-info">
                    <span class="duplicate-id">{{ person.id }}</span>
                    <span class="duplicate-created">{{ $t('FORM.LABELS.CREATED') }}: {{ person.created }}</span>
                    <span class="duplicate-counts">
                        {{ person.identification_count }} {{ $t('TREE.IDENTIFICATION') }} ·
                        {{ person.employment_count }} {{ $t('TREE.EMPLOYMENT_STATUS') }} ·
                        {{ person.document_count }} {{ $t('FORM.LABELS.DOCUMENT') }}
                    </span>
                </div>
                <div class="duplicate-candidate-actions">
                    <Button icon="pi pi-eye" text @click="gotoView(person.id)" />
                    <Button icon="pi pi-trash" severity="danger" text @click="askDelete(person)" :title="$t('FORM.BUTTONS.DELETE')" />
                </div>
            </div>
        </div>

            <ConfirmModal message="FORM.DIALOGS.CONFIRM_DELETE" :close="closeConfirm" :display="displayConfirm" />
        </template>
    </div>
</template>

<style scoped>
.empty-state {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    padding: 2rem;
    color: var(--text-color-secondary);
}

.duplicate-group {
    border: 1px solid var(--surface-border);
    border-radius: 10px;
    margin-bottom: 1rem;
    overflow: hidden;
}

.duplicate-group-header {
    background: var(--surface-50, #f8fafc);
    padding: 0.75rem 1rem;
    font-weight: 600;
}

.duplicate-candidate {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0.75rem 1rem;
    border-top: 1px solid var(--surface-border);
}

.duplicate-candidate-info {
    display: flex;
    flex-direction: column;
    gap: 0.15rem;
    font-size: 0.9rem;
}

.duplicate-id {
    font-weight: 500;
}

.duplicate-created,
.duplicate-counts {
    color: var(--text-color-secondary);
    font-size: 0.8rem;
}
</style>
