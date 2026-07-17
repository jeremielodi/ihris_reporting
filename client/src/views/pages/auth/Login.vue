<template>
  <div class="login-page flex align-items-center justify-content-center min-h-screen min-w-screen overflow-hidden">
    <div class="login-card surface-card border-round-2xl py-7 px-5 sm:px-7">
      <div class="text-center mb-5">
        <div class="logo-badge mx-auto mb-3 flex align-items-center justify-content-center">
          <img
            v-if="appSetting && appSetting.logo"
            :src="server + 'uploads/' + appSetting.logo"
            alt="Logo"
            class="logo-image"
          />
          <i v-else class="pi pi-building text-3xl" />
        </div>
        <div class="text-900 text-3xl font-semibold mb-2">
          {{ (appSetting && appSetting.app_name) || 'IHRIS Reporting' }}
        </div>
        <span class="text-600">Connectez-vous pour continuer</span>
      </div>

      <form class="flex flex-column gap-2" @submit.prevent="login">
        <label for="username" class="block font-medium text-700 mb-1">Nom d'utilisateur</label>
        <IconField class="mb-2">
          <InputIcon class="pi pi-user" />
          <InputText
            id="username"
            v-model="username"
            type="text"
            placeholder="Nom d'utilisateur"
            class="w-full"
            :invalid="usernameInvalid"
            autocomplete="username"
          />
        </IconField>

        <label for="password" class="block font-medium text-700 mb-1">Mot de passe</label>
        <IconField class="mb-3">
          <InputIcon class="pi pi-lock" />
          <Password
            id="password"
            v-model="password"
            :feedback="false"
            :toggleMask="true"
            class="w-full"
            input-class="w-full"
            :invalid="passwordInvalid"
            autocomplete="current-password"
          />
        </IconField>

        <Message v-if="errorDisplay" severity="error" :closable="false" class="mb-3">
          {{ errorDisplay }}
        </Message>

        <Button
          type="submit"
          data-testid="submit"
          :loading="loading"
          :disabled="loading"
          label="Se connecter"
          class="w-full p-3 border-round-xl"
        />
      </form>
    </div>
  </div>

  <AppConfig simple />
</template>

<script lang="ts">
import { defineComponent } from "vue";
import AppConfig from "@/layout/AppConfig.vue";
import apiService from "@/service/ApiService";
import InputText from "primevue/inputtext";
import Password from "primevue/password";
import Button from "primevue/button";
import Message from "primevue/message";
import IconField from "primevue/iconfield";
import InputIcon from "primevue/inputicon";
import SettingService from '@/views/pages/manage/setting/setting.service';
import UserService from '@/views/pages/manage/user/user.service';

interface LoginResponse {
  token: string;
  refresh_token: string;
  username: string;
  user_id:string,
  validator?: string;
  access: {
    access_facility: { id: string; name: string };
    access_facility_type?: string;
    access_facility_target?: string;
    facility_parents?: unknown;
  };
}

export default defineComponent({
  name: "LoginPage",
  components: { AppConfig, InputText, Password, Button, Message, IconField, InputIcon },
  data() {
    return {
      loading: false as boolean,
      username: "" as string,
      password: "" as string,
      errorMsg: "" as string,
      validationError: "" as string,
      server: import.meta.env.VITE_SERVER_URL,
      appSetting: null,
    };
  },
  computed: {
    errorDisplay(): string {
      return this.errorMsg || this.validationError;
    },
    usernameInvalid(): boolean {
      return this.username.trim().length < 1;
    },
    passwordInvalid(): boolean {
      return this.password.trim().length < 1;
    },
  },
  created() {
      this.loadSettings();
  },
  methods: {
    loadSettings(){
       SettingService.read(1).then((res) => {
        this.appSetting = res;
      }).catch(() => {
        // Branding is best-effort; fall back to the default title/icon.
      });
    },
    async login() {
      this.validationError = "";
      this.errorMsg = "";

      if (this.usernameInvalid || this.passwordInvalid) {
        this.validationError = "Nom d’utilisateur ou mot de passe non valide.";

        return;
      }

      this.loading = true;
      try {
        // Send credentials in POST body (safer than query string)
        const res = await UserService.users.login({
          username: this.username,
          password: this.password,
        });
        this.storeToken(res);
        this.$router.push("/");
      } catch (err: any) {
        const code = err?.code as string | undefined;
        const status = err?.response?.status as number | undefined;

        if (code === "ERR_NETWORK") {
          this.errorMsg = "Impossible de se connecter à internet.";
        } else if (status === 401) {
          this.errorMsg = "Nom d’utilisateur ou mot de passe non valide.";
        } else {
          this.errorMsg = "Échec de connexion.";
        }
      } finally {
        this.loading = false;
      }
    },

    storeToken(data: LoginResponse) {
      localStorage.setItem("_vlogin", "1");
      localStorage.setItem("_ihris_token", data.token);
      if (data.refresh_token) {
        localStorage.setItem("_ihris_refresh_token", data.refresh_token);
      }
      localStorage.setItem("_ihris_username", data.username);
      localStorage.setItem("_ihris_user_id", data.user_id);
      if (data.access?.access_facility) {
        localStorage.setItem("_access_facility_id", data.access.access_facility.id);
        localStorage.setItem("_access_facility_name", data.access.access_facility.name);
      }
      if (data.access?.access_facility_type) {
        localStorage.setItem("_access_facility_type", data.access.access_facility_type);
      }
      if (data.access?.access_facility_target) {
        localStorage.setItem("_access_facility_target", data.access.access_facility_target);
      }
      if (data.access?.facility_parents !== undefined) {
        localStorage.setItem("_access_facility_parents", JSON.stringify(data.access.facility_parents));
      }
      if (data.validator !== undefined) {
        localStorage.setItem("validator", data.validator);
      }

    },
  },
});
</script>

<style scoped>
.login-page {
  background: radial-gradient(circle at top left, #e0f2fe 0%, #eef2ff 45%, #f8fafc 100%);
}
.login-card {
  width: 100%;
  max-width: 32rem;
  box-shadow: 0 20px 45px -12px rgba(15, 23, 42, 0.18);
}
.logo-badge {
  width: 4.5rem;
  height: 4.5rem;
  border-radius: 50%;
  background: var(--primary-color, #6366f1);
  color: var(--primary-color-text, #ffffff);
  overflow: hidden;
}
.logo-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
}
:deep(.p-inputtext),
:deep(.p-password-input) {
  padding-top: 0.85rem;
  padding-bottom: 0.85rem;
  border-radius: 0.75rem;
}
:deep(.p-message) {
  border-radius: 0.75rem;
}
</style>
