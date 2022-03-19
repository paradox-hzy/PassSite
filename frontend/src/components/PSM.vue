<template>
  <div>
    <div class="mar-large full-width font-normal">
      <div class="mar-large">
        <p>
          &nbsp;&nbsp;&nbsp;我们的口令强度评估器包括用蒙特卡洛方法对口令集中口令强度的评估和基于概率上下文无关文法(PCFG)的对集合外口令的强度评估以及基于口令规则的赋分三个部分。
        </p>
         <p>
          &nbsp;&nbsp;&nbsp;蒙特卡洛方法中，使用A-Res算法对口令集进行采样，并计算样本集合中口令的势，当选取的样本量n趋向于无穷大时，其标准差趋向于0，势趋向于口令强度Sp(a)，口令的势就可以较为准确地表示口令的强度。
        </p>
        <p>
          &nbsp;&nbsp;&nbsp;对于不在生成口令集中的口令，我们采用概率上下文无关法进行强度评估，通过对真实口令集的训练统计出口令模式频率表和语义频率表，并据此生成带频率猜测的集合以模拟现实中口令的概率分布。然后根据上述的统计结果对需要评估的口令进行概率计算。
        </p>
        <p>
          &nbsp;&nbsp;&nbsp;由于上述方法均无法覆盖所有用户可能输入的口令，故引入第三种方法，通过对口令规则的赋分来补充评估。口令规则考虑了以下五个方面：口令长度、字母大小写、数字长度、特殊字符长度以及口令中含有的字符种类。
        </p>
      </div>
    </div>
    <div class="pad mar-large shadow border-radius font-normal bac">
      <div class="full-width">
        <div class="mar-large">
          <div class="mar-small">密码：</div>
          <div class="mar-small">
            <el-input
              v-model="password"
              placeholder="请输入需要进行强度评测的密码"
            ></el-input>
          </div>
        </div>

        <div class="mar-large">
          <el-button
            class="mar-small"
            type="primary"
            @click="submit"
            :loading="isloading"
            >提交</el-button
          >
        </div>

        <div class="mar-large">
          <el-rate
            class="mar-large"
            v-show="showresult"
            v-model="result"
            disabled
            :max="10"
            show-score
            :allow-half="true"
            text-color="#ff9900"
            score-template="{value}"
          >
          </el-rate>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from "axios";
import Qs from "qs";
import { Message } from "element-ui";
export default {
  data() {
    return {
      password: null,
      isloading: false,
      showresult: false,
      result: 0,
    };
  },
  methods: {
    toJson: function () {
      return "module:psm,password:" + this.password;
    },
    check: function () {
      var ok =
        !!this.password &&
        this.password.length > 0 &&
        this.password.length < 100;
      if (!ok) {
        Message.error("输入密码不符合要求");
      }
      return ok;
    },
    submit: function () {
      if (this.check()) {
        this.isloading = true;
        this.showresult = false;
        // console.log(this.toJson())
        let payload = {
          msg: this.toJson(),
        };
        axios({
          method: "get",
          params: payload,
          url: "http://localhost:8000/server/server",
        }).then(
            res => {
                this.result = parseFloat(res.data)/10;
                this.showresult = true;
                this.isloading = false;
            }
        )
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
</style>
