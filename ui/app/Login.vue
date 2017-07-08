<template>
  <v-app>
    <main>
      <v-container fluid>
        <h4 class="login-header">API Gateway</h4>
        <v-card class="login-card">
          <v-container fluid grid-list-lg>
            <v-layout row>
              <v-flex xs12>
                <v-text-field
                  name="username"
                  label="Username"
                  id="username"></v-text-field>
              </v-flex>
            </v-layout>
            <v-layout row>
              <v-flex xs12>
                <v-text-field
                  type="password"
                  name="password"
                  label="Password"
                  id="password"></v-text-field>
              </v-flex>
            </v-layout>
          </v-container>
          <v-card-actions>
            <v-spacer></v-spacer>
            <v-btn primary>Login</v-btn>
          </v-card-actions>
        </v-card>
      </v-container>
    </main>
  </v-app>
</template>

<script>
  export default {
    data () {
      return {
      }
    }
  }
</script>

<style lang="stylus">
  @import '../node_modules/vuetify/src/stylus/main'

  .application--light {
    background: #ffffff;
  }

  .login-header {
    text-align: center;
    margin-bottom: 30px;
  }

  .login-card {
    width: 320px;
    margin: 0 auto;
  }
</style>
