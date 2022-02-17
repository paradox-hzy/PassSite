<template>
  <div>
    <div>
      <h1 class="title">口令生成展示平台</h1>
    </div>
    <div class="mar">
      <el-tabs tab-position="top" class="full-height shadow" type="card">
        <el-tab-pane label="LSTM模型">
          <LSTM></LSTM>
        </el-tab-pane>
        <el-tab-pane label="PL模型">
          <PL></PL>
        </el-tab-pane>
        <el-tab-pane label="PassGAN模型">
          <PassGAN></PassGAN>
        </el-tab-pane>
        <el-tab-pane label="PSM">
          <PSM></PSM>
        </el-tab-pane>
      </el-tabs>
    </div>
  </div>
</template>

<script>
import LSTM from "../components/LSTM.vue";
import PL from "../components/PL.vue";
import PassGAN from "../components/PassGAN.vue";
import PSM from "../components/PSM.vue"
export default {
  components: {
    LSTM,
    PL,
    PassGAN,
    PSM,
  },
};
</script>


<style scoped>
.title {
  margin: 30px;
  color: var(--black);
  font-size: 50px;
}
.mar {
    margin: 10px 10px 30px 10px;
}
</style>