<template>
    <div>
        <youtube :video-id="videoId" ref="youtube" @playing="playing" @ready="readyHandler" @paused="paused"></youtube>
        <button @click="playVideo">play</button>
    </div>
</template>

<script>
    import axios from 'axios';

    const headers = {
        'Content-Type': 'application/json',
    }

    export default {
        name: 'YouTube',

        data() {
            return {
                videoId: 'VetJa7a7gFs',
                player: null
            }
        },

        methods: {
            async readyHandler() {
                this.player = this.$refs.youtube.player;

                axios({
                    method: 'post',
                    url: 'http://10.84.113.245:2000/api/video',
                    data: await this.player.getDuration(),
                    headers: headers
                });
            },

            async handleState() {
                const state = await this.player.getPlayerState();
                const time = await this.player.getCurrentTime();
                console.log(this.player.getVideoData);

                axios({
                    method: 'post',
                    url: 'http://10.84.113.245:2000/api/video_state',
                    data:  {
                        video_name: 'kek',
                        current_time: time,
                        current_state: state
                    },
                    headers: headers
                })
            },

            playVideo() {
                this.player.playVideo()
            },

            paused(e) {
                this.handleState();
                clearInterval(this.interval);
            },

            playing(e) {
                this.interval = setInterval(this.handleState, 1000)
            }
        },

        mounted() {
            clearInterval(this.interval);
        }
    }
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped lang="scss">
h3 {
  margin: 40px 0 0;
}
ul {
  list-style-type: none;
  padding: 0;
}
li {
  display: inline-block;
  margin: 0 10px;
}
a {
  color: #42b983;
}
</style>
