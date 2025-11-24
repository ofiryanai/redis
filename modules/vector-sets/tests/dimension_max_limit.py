from test import TestCase, generate_random_vector
import struct
import redis.exceptions

MAX_DIM = 65536


class DimensionMaxLimit(TestCase):
    def getname(self):
        return "[regression] HNSW maximum dimension limit enforcement"

    def estimated_runtime(self):
        return 0.5
    def test(self):
        # Run all dimension limit tests
        self.test_boundary_without_reduce_fp32()
        self.test_boundary_with_reduce_values()
        self.test_vsim_query_too_large()



    def test_boundary_without_reduce_fp32(self):
        key = self.test_key + ":maxdim"
        # dim = MAX_DIM should be accepted
        dim_ok = MAX_DIM
        vec_ok = generate_random_vector(dim_ok)
        vec_ok_bytes = struct.pack(f"{dim_ok}f", *vec_ok)
        res = self.redis.execute_command("VADD", key, "FP32", vec_ok_bytes, f"{key}:ok")
        assert res == 1

        # dim = MAX_DIM + 1 should be rejected
        dim_bad = MAX_DIM + 1
        vec_bad = generate_random_vector(dim_bad)
        vec_bad_bytes = struct.pack(f"{dim_bad}f", *vec_bad)
        try:
            self.redis.execute_command("VADD", key, "FP32", vec_bad_bytes, f"{key}:bad")
            assert False, "VADD with dimension > MAX_DIM should fail"
        except redis.exceptions.ResponseError as e:
            # Exceeding the max dimension is treated as a generic invalid
            # vector specification error by VADD/parseVector.
            assert "invalid vector specification" in str(e)

    def test_boundary_with_reduce_values(self):
        # original dim at boundary, but keep projected dim small to avoid huge matrices
        original_dim = MAX_DIM
        reduced_dim = 16
        vec = generate_random_vector(original_dim)
        args = ["VADD", self.test_key + ":reduce", "REDUCE", reduced_dim, "VALUES", original_dim]
        args.extend(str(x) for x in vec)
        res = self.redis.execute_command(*args, f"{self.test_key}:ele1")
        assert res == 1

        # reduced dim above boundary should fail at parse time; original_dim can be small here
        small_original_dim = 4
        too_big_reduce = MAX_DIM + 1
        vec2 = generate_random_vector(small_original_dim)
        args2 = ["VADD", self.test_key + ":reduce2", "REDUCE", too_big_reduce, "VALUES", small_original_dim]
        args2.extend(str(x) for x in vec2)
        try:
            self.redis.execute_command(*args2, f"{self.test_key}:ele2")
            assert False, "VADD with REDUCE dim > MAX_DIM should fail"
        except redis.exceptions.ResponseError as e:
            assert "invalid vector specification" in str(e)

    def test_vsim_query_too_large(self):
        # Create a small set
        dim = 4
        vec = generate_random_vector(dim)
        vec_bytes = struct.pack("4f", *vec)
        res = self.redis.execute_command("VADD", self.test_key, "FP32", vec_bytes, f"{self.test_key}:base")
        assert res == 1

        # Query with oversized VALUES vector should fail
        qdim = MAX_DIM + 1
        qvec = generate_random_vector(qdim)
        args = ["VSIM", self.test_key, "VALUES", qdim]
        args.extend(str(x) for x in qvec)
        try:
            self.redis.execute_command(*args, "COUNT", 1)
            assert False, "VSIM with dimension > MAX_DIM should fail"
        except redis.exceptions.ResponseError as e:
            assert "invalid vector specification" in str(e)

