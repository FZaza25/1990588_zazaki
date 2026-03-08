<template>
  <div>
    <v-dialog
        v-model="modal"
        persistent
        no-click-animation
        scrollable
        scroll-strategy="none"
        content-class="central-modal-content"
        :content-props="{ style: overlayStyle }"
    >
      <div>
        <div class="bg-background border-b cursor-move" @mousedown.prevent="startDrag($event)">
          <div class="d-flex w-100 justify-space-between py-2 px-4">
            <slot name="header" ></slot>
            <v-icon icon="mdi-close"  size="32" @click="close()"/>
          </div>

        </div>

        <div class="d-flex flex-column bg-background overflow-y-auto">
          <div class="px-4 py-2">
            <slot name="content"></slot>
          </div>
        </div>
        <div class="d-flex w-100">
          <div class="bg-background w-100 py-5 px-4 border-t">
            <slot name="footer"></slot>
          </div>
        </div>
      </div>

    </v-dialog>
  </div>
</template>

<script>

export default {
  props: ['args', 'size', 'scrollClass'],
  data() {
    return {
      modal: false,
      side: true,

      dragging: false,

      x: 0,
      y: 0,

      offsetX: 0,
      offsetY: 0,


    }
  },
  computed: {
    overlayStyle() {
      return {
        position: 'fixed',
        inset: 'auto',
        margin: '0',
        transform: 'none',
        left: `${this.x}px`,
        top: `${this.y}px`,
        minWidth: '50%',
        width: '50%'
      }
    }
  },
  methods: {
    startDrag(event) {
      this.dragging = true
      this.offsetX = event.clientX - this.x
      this.offsetY = event.clientY - this.y

      document.body.style.userSelect = 'none'

      window.addEventListener('mousemove', this.onDrag)
      window.addEventListener('mouseup', this.stopDrag)

    },
    onDrag(event) {
      if(!this.dragging) {
        return
      }
      this.x = event.clientX - this.offsetX
      this.y = event.clientY - this.offsetY
    },
    stopDrag(){
      this.dragging = false

      document.body.style.userSelect = ''
      window.removeEventListener('mousemove', this.onDrag)
      window.removeEventListener('mouseup', this.stopDrag)
    },
    open() {
      this.modal = true
      this.$nextTick(() => {
        const el = document.querySelector('.v-overlay__content.central-modal-content')
        if (!el) return
        const rect = el.getBoundingClientRect()
        this.x = (window.innerWidth - rect.width) / 2
        this.y = (window.innerHeight - rect.height) / 2
      })
    },
    close() {
      this.modal = false
      this.stopDrag()
      this.$emit('close')
    }
  },
  beforeUnmount() {
    window.removeEventListener('mousemove', this.onDrag)
    window.removeEventListener('mouseup', this.stopDrag)
  }
}
</script>

