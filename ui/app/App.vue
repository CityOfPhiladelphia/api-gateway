<template>
  <v-app>
    <v-navigation-drawer
      persistent
      clipped
      v-model="drawer">
      <v-list>
        <v-list-tile
          v-for="(item, i) in items"
          :key="i"
          value="true"
          v-bind:to="item.to">
          <v-list-tile-action>
            <v-icon>{{ item.icon }}</v-icon>
          </v-list-tile-action>
          <v-list-tile-content>
            <v-list-tile-title>{{ item.title }}</v-list-tile-title>
          </v-list-tile-content>
        </v-list-tile>
      </v-list>
    </v-navigation-drawer>
    <v-toolbar dark class="primary">
      <v-toolbar-side-icon @click.native.stop="drawer = !drawer"></v-toolbar-side-icon>
      <v-toolbar-title v-text="$route.meta.title"></v-toolbar-title>
    </v-toolbar>
    <main>
      <v-container fluid>
        <v-slide-y-transition mode="out-in">
          <router-view></router-view>
        </v-slide-y-transition>
      </v-container>
    </main>
  </v-app>
</template>

<script>
  export default {
    data () {
      return {
        drawer: true,
        items: [
          {
            icon: 'dashboard',
            title: 'Dashboard',
            to: '/dashboard'
          },
          {
            icon: 'dns', // extension, dns, settings_input_component, settings_system_daydream
            title: 'API Endpoints',
            to: '/endpoints'
          },
          {
            icon: 'vpn_keys',
            title: 'Keys',
            to: '/keys'
          },
          {
            icon: 'block',
            title: 'Bans',
            to: '/bans'
          }
        ],
        title: 'Dashboard'
      }
    }
  }
</script>

<style lang="stylus">
  @import '../node_modules/vuetify/src/stylus/main'

  .application--light {
    background: #ffffff;
  }

  .navigation-drawer {
    width: 220px;
  }

  .navigation-drawer--persistent.navigation-drawer--open:not(.navigation-drawer--is-mobile):not(.navigation-drawer--right):not(.navigation-drawer--clipped) ~ .toolbar, .navigation-drawer--persistent.navigation-drawer--open:not(.navigation-drawer--is-mobile):not(.navigation-drawer--right) ~ main, .navigation-drawer--persistent.navigation-drawer--open:not(.navigation-drawer--is-mobile):not(.navigation-drawer--right) ~ .footer:not(.footer--fixed):not(.footer--absolute) {
    padding-left: 220px;
  }
</style>