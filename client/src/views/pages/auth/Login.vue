<template>
  <div class="surface-ground flex align-items-center justify-content-center min-h-screen min-w-screen overflow-hidden">
    <div class="flex flex-column align-items-center justify-content-center">
      <div>
        <form @submit.prevent="login" style="width: 100%">
          <div class="w-full surface-card py-8 px-5 sm:px-6 border-round-2xl" style="border-radius: 3px">
            <div class="text-center mb-5" v-if="appSetting">
              <img :src="server + 'uploads/'+ appSetting.logo" alt="Image" height="70" class="mb-3" />
              <div class="text-900 text-3xl font-medium mb-3">{{appSetting.app_name || 'IHRIS Reporting'}}</div>
              <span class="text-600 font-medium">Connectez-vous pour continuer</span>
            </div>

            <div class="flex flex-column gap-1">
              <label for="username" class="block text-xl font-medium m-2">Nom d'utilisateur</label>
              <InputText
                id="username"
                v-model="username"
                type="text"
                placeholder="Nom d'utilisateur"
                class="w-full md:w-30rem mb-1 border-round-3xl"
                :invalid="usernameInvalid"
                style="padding: 1rem"
                autocomplete="username"
              />

              <label for="password" class="block font-medium text-xl m-2">Mot de passe</label>
              <Password
                id="password"
                v-model="password"
                :feedback="false"
                :toggleMask="true"
                class="w-full mb-3"
                inputClass="w-full border-round-3xl"
                :inputStyle="{ padding: '1rem' }"
                :invalid="passwordInvalid"
                autocomplete="current-password"
              />

              <div class="flex align-items-center justify-content-between mb-5 ml-2 gap-5">
                <small class="text-pink-800">{{ errorMsg || validationError }}</small>
              </div>

              <Button
                :loading="loading"
                :disabled="loading"
                label="Se connecter"
                class="w-full p-3 border-round-3xl"
                type="submit"
              />
            </div>
          </div>
        </form>
      </div>
    </div>
  </div>

  <AppConfig simple />
</template>

<script lang="ts">
import { defineComponent } from "vue";
import AppConfig from "@/layout/AppConfig.vue";
import apiService from "@/service/ApiService";
import router from "@/router"; // adjust if your path differs
import InputText from "primevue/inputtext";
import Password from "primevue/password";
import Button from "primevue/button";
import SettingService from '@/views/pages/manage/setting/setting.service';

interface LoginResponse {
  token: string;
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
  components: { AppConfig, InputText, Password, Button },
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
      })
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
        const res = await apiService.post<LoginResponse>("/users/reporting/login", {
          username: this.username,
          password: this.password,
        });
        this.storeToken(res.data);
        window.location = '/';
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
.pi-eye,
.pi-eye-slash {
  transform: scale(1.6);
  margin-right: 1rem;
}
.text-pink-800 {
  color: #9d174d;
}
</style>
