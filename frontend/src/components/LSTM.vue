<template>
  <div>
    <div class="mar-large full-width font-normal">
      <div class="mar-large">
        <p>
          &nbsp;&nbsp;&nbsp;循环神经网络(RNN)及其变体，如长短期记忆网络(LSTM)和门递归单元(GRU)，都可以用于口令猜测。一个简单的RNN网络的结构包含输入层、隐藏侧、输出层，设输入为一个序列x1x2x3...xn，在网络训练时也是按照x1到xn的顺序进行。
        </p>

        <p>
          &nbsp;&nbsp;&nbsp;隐藏层神经元具有一个隐藏状态，初始时设置为h0，根据输入的序列不断进行更新：h1=f(Ux1+Wh0+b)。这里的U、W、b都是参数，并且针对不同的序列单元都是相同的。依次递推算出h2=f(Ux2+Wh1+b)，h3，直到hn。根据隐藏层状态获取对应的输出y，公式如下：y1=softmax(Vh1+c)。这里的V、c都是参数，并且针对不同的序列单元都是相同的。同样递推算出y2，y3，直到yn。为了避免梯度消失问题，我们统一使用LSTM而不是RNN。在训练模型时，通常对口令中的每个字符进行独热码编码，以便将口令字符串转换为矩阵。此外，由于LSTM是监督学习方法，需要为输入口令x构造相应的值y。如下图所示：
        </p>

        <div class="text-center">
          <img src="../assets/lstm.png" class="half-width" />
        </div>

        <p>
          &nbsp;&nbsp;&nbsp;在这里，使用一个例子来说明训练的过程。假设字符集是{a、b、c、Bos、Eos}，其中Bos表示口令的开始，Eos表示口令的结束。口令“abc”被转换为一个矩阵：[[0,0,0,1,0]，[1,0,0,0,0]，[0,1,0,0,0]，[0,0,1,0,0]]，，可以看作是输入x。对应的值y为：[[1,0,0,0,0]，[0,1,0,0,0]，[0,0,1,0,0]，[0,0,0,0,1]]。
        </p>

        <p>
          &nbsp;&nbsp;&nbsp;基于LSTM的模型是一种将概率分配给猜测口令的概率模型。通过将口令字符串的前缀输入LSTM，得到下一个字符的概率。例如，一个口令生成过程可以是：“B”-“Ba”-“Bab”-“Babc”-“BabcE”，这里每次选择概率最高的字符作为字符串的下一个字符。以字符作为最小单元进行训练和生成的模型可以被视为字符级别的（character-level）。
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
          <div class="mar-small">
            生成口令的概率阈值下限x：（以10^(-x)为单位）
          </div>
          <div class="mar-small">
            <el-input
              v-model="prob"
              :placeholder="'输入范围' + this.PROB_MIN + '-' + this.PROB_MAX"
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
  EPOCH_MIN,
  EPOCH_MAX,
  PROB_MIN,
  PROB_MAX,
  GEN_NUM_MIN,
  GEN_NUM_MAX,
  SEQ_MINLEN_MIN,
  SEQ_MINLEN_MAX,
} from "../constant/parameters";
import { Message } from "element-ui";
export default {
  data() {
    return {
      EPOCH_MIN: EPOCH_MIN,
      EPOCH_MAX: EPOCH_MAX,
      PROB_MIN: PROB_MIN,
      PROB_MAX: PROB_MAX,
      GEN_NUM_MIN: GEN_NUM_MIN,
      GEN_NUM_MAX: GEN_NUM_MAX,
      SEQ_MINLEN_MIN: SEQ_MINLEN_MIN,
      SEQ_MINLEN_MAX: SEQ_MINLEN_MAX,
      type: "gen",
      email: null,
      epoch: null,
      prob: null,
      num: null,
      len: null,
      error: "",
      dialogVisible: false,
    };
  },
  methods: {
    toJson: function () {
      return (
        "module:lstm,type:" +
        this.type +
        ",email:" +
        this.email +
        ",epoch:" +
        (this.type == "train" ? this.epoch : 0) +
        ",prob:" +
        this.prob +
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
      // epoch
      const digits_re = /\d/;
      if (
        this.type === "train" &&
        (!digits_re.test(this.epoch) ||
          this.epoch < this.EPOCH_MIN ||
          this.epoch > this.EPOCH_MAX)
      ) {
        this.error += "训练轮数错误，";
      }
      // prob
      if (
        !digits_re.test(this.prob) ||
        this.prob < this.PROB_MIN ||
        this.prob > this.PROB_MAX
      ) {
        this.error += "概率阈值下限错误，";
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
