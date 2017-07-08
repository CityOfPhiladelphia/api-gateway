<template>
  <v-app>
    <main>
      <v-container fluid>
        <h4>API Gateway</h4>
        <v-layout>
          <v-flex xs4 offset-xs4>
            <v-card>
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
                <v-layout row>
                  <v-flex xs2 offset-xs8>
                    <v-btn light primary>Login</v-btn>
                  </v-flex>
                </v-layout>
              </v-container>
            </v-card>
          </v-flex>
        </v-layout>
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

  h4 {
    text-align: center
  }
</style>
