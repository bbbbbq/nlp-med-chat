<template>
  <div class="auth-container">
    <div class="form-container">
      <div class="auth-form">
        <div class="auth-header">
          <h2>我们是 aroma</h2>
          <p>欢迎回来，请登录您的帐户。</p>
        </div>
        <form @submit.prevent="login" autocomplete="off">
          <div class="form-group">
            <input type="text" id="username" v-model="username" required readonly onfocus="this.removeAttribute('readonly');" autocomplete="new-password">
            <label for="username">用户名</label>
          </div>
          <div class="form-group">
            <input type="password" id="password" v-model="password" required readonly onfocus="this.removeAttribute('readonly');" autocomplete="new-password">
            <label for="password">密码</label>
          </div>
          <!-- Options like 'Remember me' can be added back here if needed -->
          <div class="button-group">
            <button type="submit" class="btn btn-primary">登录</button>
            <router-link to="/register" class="btn btn-secondary">注册</router-link>
          </div>
          <p v-if="error" class="error-message">{{ error }}</p>
        </form>
        <!-- Terms and conditions can be added back here if needed -->
      </div>
    </div>
    <div class="image-container" :style="{ backgroundImage: 'url(https://images.pexels.com/photos/807598/pexels-photo-807598.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=2)' }">
    </div>
  </div>
</template>

<script>
import axios from 'axios';
import { useRouter } from 'vue-router';

export default {
  setup() {
    const router = useRouter();
    return { router };
  },
  data() {
    return {
      username: '',
      password: '',
      error: ''
    };
  },
  methods: {
    async login() {
      this.error = '';
      try {
        const response = await axios.post('http://localhost:3000/login', {
          username: this.username,
          password: this.password
        });

        if (response.data.success) {
          // Store role in localStorage
          localStorage.setItem('userRole', response.data.role);

          if (response.data.role === 'admin' || response.data.role === 'doctor') {
            this.$router.push('/admin/dashboard');
          } else {
            this.error = '无法识别的用户角色。';
          }
        } else {
          this.error = response.data.message;
        }
      } catch (err) {
        console.error('登录请求失败:', err);
        this.error = '登录失败，请稍后再试。';
      }
    }
  }
};
</script>

<style scoped>
@import '../assets/form-styles.css';
</style>
