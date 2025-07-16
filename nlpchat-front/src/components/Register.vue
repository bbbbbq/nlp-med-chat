<template>
  <div class="auth-container">
    <div class="form-container">
      <div class="auth-form">
        <div class="auth-header">
          <h2>创建新帐户</h2>
          <p>加入我们，开启新旅程。</p>
          <p style="text-align: left; color: #6c757d; margin-top: -1.5rem; margin-bottom: 2.5rem;">请注意：当前仅开放医生帐户注册。</p>
        </div>
        <form @submit.prevent="register" autocomplete="off">
          <div class="form-group">
            <input type="text" id="username" v-model="username" required readonly onfocus="this.removeAttribute('readonly');" autocomplete="new-password">
            <label for="username">用户名</label>    
          </div>
          <div class="form-group">
            <input type="password" id="password" v-model="password" required readonly onfocus="this.removeAttribute('readonly');" autocomplete="new-password">
            <label for="password">密码</label>
          </div>
          <div class="form-group">
            <input type="password" id="confirmPassword" v-model="confirmPassword" required readonly onfocus="this.removeAttribute('readonly');" autocomplete="new-password">
            <label for="confirmPassword">确认密码</label>
          </div>
          <div class="button-group">
            <button type="submit" class="btn btn-primary">注册</button>
          </div>
        </form>
        <div class="login-link">
          已经有帐户了？ <router-link to="/login">立即登录</router-link>
        </div>
        <p v-if="message" :class="isError ? 'error-message' : 'success-message'">{{ message }}</p>
      </div>
    </div>
    <div class="image-container" :style="{ backgroundImage: 'url(https://images.pexels.com/photos/1072179/pexels-photo-1072179.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=2)' }">
    </div>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  data() {
    return {
      username: '',
      password: '',
      confirmPassword: '',
      message: '',
      isError: false
    };
  },
  methods: {
    async register() {
      this.message = '';
      if (this.password !== this.confirmPassword) {
        this.isError = true;
        this.message = '两次输入的密码不一致。';
        return;
      }

      try {
        const response = await axios.post('http://localhost:3000/register', {
          username: this.username,
          password: this.password
        });

        if (response.data.message === '注册成功') {
          this.isError = false;
          this.message = '注册成功！正在跳转到登录页面...';
          setTimeout(() => {
            this.$router.push('/login');
          }, 2000);
        } else {
          this.isError = true;
          this.message = response.data.message;
        }
      } catch (err) {
        this.isError = true;
        console.error('注册请求失败:', err);
        this.message = '注册失败，请稍后再试。';
      }
    }
  }
};
</script>

<style scoped>
@import '../assets/form-styles.css';
</style>
