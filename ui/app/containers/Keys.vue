<template>
  <v-data-table
      v-bind:headers="headers"
      :items="keys"
      hide-actions
      v-model="selected"
      selected-key="id"
      select-all
      class="elevation-1">
    <template slot="items" scope="props">
      <td>
        <v-checkbox
          primary
          hide-details
          v-model="props.selected"
        ></v-checkbox>
      </td>
      <td>{{ props.item.id }}</td>
      <td>{{ props.item.active }}</td>
      <td>{{ props.item.owner_name }}</td>
      <td>{{ props.item.contact_email }}</td>
      <td>{{ props.item.contact_name }}</td>
      <td>{{ props.item.created_at | moment('DD/MM/YYYY hh:mm:ss A z') }}</td>
      <td>{{ props.item.updated_at | moment('DD/MM/YYYY hh:mm:ss A z') }}</td>
    </template>
  </v-data-table>
</template>

<script>
  export default {
    data () {
      return {
        selected: [],
        headers: [
          {
            text: 'ID',
            align: 'left',
            value: 'id'
          },
          {
            text: 'Active',
            align: 'left',
            value: 'active'
          },
          {
            text: 'Owner Name',
            align: 'left',
            value: 'owner_name'
          },
          {
            text: 'Contact Email',
            align: 'left',
            value: 'contact_email'
          },
          {
            text: 'Contact Name',
            align: 'left',
            value: 'contact_name'
          },
          {
            text: 'Created At',
            align: 'left',
            value: 'created_at'
          },
          {
            text: 'Updated At',
            align: 'left',
            value: 'updated_at'
          }
        ],
        keys: [
          {
            id: 1,
            active: true,
            owner_name: 'John Doe',
            contact_email: 'john.doe@example.com',
            contact_name: null,
            updated_at: '2017-07-08T14:20:19.564447+00:00',
            created_at: '2017-07-08T14:20:19.564447+00:00'
          },
          {
            id: 2,
            active: true,
            owner_name: 'Jane Doe',
            contact_email: 'jane.doe@example.com',
            contact_name: null,
            updated_at: '2016-08-05T14:20:19.564447+00:00',
            created_at: '2016-08-05T14:20:19.564447+00:00'
          }
        ]
      }
    }
  }
</script>

<style lang="css">

</style>