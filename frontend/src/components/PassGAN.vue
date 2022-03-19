<template>
  <div>
    <div class="mar-large full-width font-normal">
      <div class="mar-large">
        <p>
          &nbsp;&nbsp;&nbsp;PassGAN模型是在生成式对抗网络(Generative Adversarial Networks，GAN)模型的基础上实现的，我们这里先对GAN模型进行介绍，它主要包含一个生成器G和一个判别器D，生成器通过训练生成接近真实密码分布的数据，并使用判别器来判断数据是来自真实密码还是来自生成器。生成器和判别器以这种方式进行反向训练，直到模型收敛，这意味着判别器不能识别生成器生成的数据。大致结构如下：
        </p>

        <div class="text-center">
          <img src="../assets/passgan.png" class="half-width" />
        </div>

        <p>
          &nbsp;&nbsp;&nbsp;输入生成器的噪声Z（noise）是符合正态分布的矩阵，输出为G(Z,theta), theta为生成器G中的参数，这里的输出即为fake data。将生成器的生成的数据和真实数据分别输入判别器，得到D(G(Z,theta),theta2)，D(Xreal,theta2)，其中theta2为判别器的参数。最终得到的loss(G)=-D(G(Z,theta),theta2)，loss(D)=D(G(Z,theta),theta2)-D(Xreal,theta2)。
        </p>

        <p>
          &nbsp;&nbsp;&nbsp;原始GAN训练起来较为困难，因此PassGAN模型的网络框架采用的是一种GAN的改进模型：WGAN-GP，该模型由由Gulrajani等人提出的。
        </p>
      </div>
    </div>
    <div class="pad mar-large shadow border-radius font-normal bac">
      <div class="full-width">
        <div class="mar-large">
          <div class="mar-small">邮箱：</div>
          <div class="mar-small">
            <el-input
              v-model="email"
              placeholder="请输入生成口令发送的目标邮箱"
            ></el-input>
          </div>
        </div>

        <div class="mar-large">
          <div class="mar-small">生成口令的个数：</div>
          <div class="mar-small">
            <el-input
              v-model="num"
              :placeholder="
                '输入范围' + this.GEN_NUM_MIN + '-' + this.GEN_NUM_MAX
              "
            ></el-input>
          </div>
        </div>

        <div class="mar-large">
          <div class="mar-small">生成口令的最小长度值：</div>
          <div class="mar-small">
            <el-input
              v-model="len"
              :placeholder="
                '输入范围' + this.SEQ_MINLEN_MIN + '-' + this.SEQ_MINLEN_MAX
              "
            ></el-input>
          </div>
        </div>

        <div class="mar-large">
          <el-button class="mar-small" type="primary" @click="submit"
            >提交</el-button
          >
        </div>
      </div>
    </div>

    <el-dialog title="提示" :visible.sync="dialogVisible" width="30%">
      <span>训练结果稍后会发送至您的邮箱，请不要重复提交！</span>
      <span slot="footer" class="dialog-footer">
        <el-button type="primary" @click="dialogVisible = false"
          >确 定</el-button
        >
      </span>
    </el-dialog>
  </div>
</template>

<script>
import axios from "axios";
import Qs from "qs";
import {
  ITER_MIN,
  ITER_MAX,
  GEN_NUM_MIN,
  GEN_NUM_MAX,
  SEQ_MINLEN_MIN,
  SEQ_MINLEN_MAX,
} from "../constant/parameters";
import { Message } from "element-ui";
export default {
  data() {
    return {
      ITER_MIN: ITER_MIN,
      ITER_MAX: ITER_MAX,
      GEN_NUM_MIN: GEN_NUM_MIN,
      GEN_NUM_MAX: GEN_NUM_MAX,
      SEQ_MINLEN_MIN: SEQ_MINLEN_MIN,
      SEQ_MINLEN_MAX: SEQ_MINLEN_MAX,
      type: "gen",
      email: null,
      iter: null,
      num: null,
      len: null,
      error: "",
      dialogVisible: false,
    };
  },
  methods: {
    toJson: function () {
      return (
        "module:gan,type:" +
        this.type +
        ",email:" +
        this.email +
        ",iter:" +
        (this.type == "train" ? this.iter : 0) +
        ",num:" +
        this.num +
        ",len:" +
        this.len
      );
    },
    check: function () {
      this.error = "";
      // emial
      const email_re =
        /^([a-zA-Z0-9]+[_|_|\-|.]?)*[a-zA-Z0-9]+@([a-zA-Z0-9]+[_|_|.]?)*[a-zA-Z0-9]+\.[a-zA-Z]{2,6}$/;
      if (this.email === null || !email_re.test(this.email)) {
        this.error += "邮箱错误，";
      }
      const digits_re = /\d/;
      // iter
      if (
        this.type === "train" &&
        (!digits_re.test(this.iter) ||
          this.iter < this.ITER_MIN ||
          this.iter > this.ITER_MAX)
      ) {
        this.error += "训练迭代次数错误，";
      }
      // num
      if (
        !digits_re.test(this.num) ||
        this.num < this.GEN_NUM_MIN ||
        this.num > this.GEN_NUM_MAX
      ) {
        this.error += "口令数量错误，";
      }
      // len
      if (
        !digits_re.test(this.len) ||
        this.len < this.SEQ_MINLEN_MIN ||
        this.len > this.SEQ_MINLEN_MAX
      ) {
        this.error += "生成口令长度下限错误，";
      }

      if (this.error !== "") {
        Message.error(this.error);
        return false;
      } else {
        return true;
      }
    },
    submit: function () {
      if (this.check()) {
        this.dialogVisible = true;
        // console.log(this.toJson());
        let payload = {
          msg: this.toJson(),
        };
        axios({
          method: "get",
          params: payload,
          url: "http://localhost:8000/server/server",
        }).then((res) => {
          console.log("业务编号: " + res.data);
        });
      }
    },
  },
};
</script>


<style scoped>
.bac {
  background-color: var(--secondary-color-2);
}
.mar-small {
  margin: 8px;
}
.mar-large {
  margin: 15px;
  margin-right: 40px;
}
.half-width {
  width: 50%;
}
.pad {
  padding: 20px 20px 40px 20px;
}
.half-width {
  width: 50%;
}
</style>
